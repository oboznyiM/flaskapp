from flask import Flask, request, jsonify, redirect
from apscheduler.schedulers.background import BackgroundScheduler
import os
from model import Instance
from health_check import update_health
import requests
import logging
import redis
from functools import wraps
import time

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)


REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)


all_instances = []
alive_instances = []

scheduler = BackgroundScheduler()
scheduler.add_job(func=update_health, trigger="interval", seconds=15)
scheduler.start()


instances = os.getenv("BACKENDS")
if instances is not None:
    for url in instances.split(","):
        all_instances.append(Instance(url))
    update_health()
current = 0


def rate_limiter(
    max_requests, expiry_time, getUserId=lambda req: req.remote_addr, key_prefix=""
):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            user_id = getUserId(request)

            key = f"{key_prefix}:{user_id}:{time.time() // expiry_time}"
            current_requests_count = r.get(key)
            if (
                current_requests_count is not None
                and int(current_requests_count) >= max_requests
            ):
                response = jsonify({"message": "Rate limit exceeded. Try again later."})
                response.status_code = 429
                return response

            else:
                current_requests_count = r.incr(key, 1)
                if current_requests_count == 1:
                    r.expire(key, expiry_time)
                logger.info(
                    f"The user {user_id} acessed the resource {request.full_path} {int(r.get(key))} times."
                )
                return f(*args, **kwargs)

        return wrapped

    return decorator


def getInstance():
    global current
    if len(alive_instances) == 0:
        return jsonify({"error": "No alive instances"}), 503

    current = current % len(alive_instances)
    instance = alive_instances[current]
    current = (current + 1) % len(alive_instances)
    logger.debug(f"[REQUEST] Request redirected to instance {instance.url}")
    return instance


@app.route("/instances", methods=["POST"])
def add_instances():
    urls = request.json
    logger.debug(f"[TEST] {urls}")
    global alive_instances
    alive_instances = []
    global all_instances
    all_instances = []
    for url in urls:
        all_instances.append(Instance(url))
    update_health()
    return jsonify({"message": "Instances added successfully"}), 200


@app.route("/instances", methods=["GET"])
def get_instances():
    return jsonify([{"url": i.url, "isAlive": i.is_alive} for i in all_instances]), 200


@app.route("/v1/coffee/favourite", methods=["POST"])
@rate_limiter(10, 60, key_prefix="favourite")
def proxy_set_favorite():
    instance = getInstance()
    return redirect(
        instance.url.replace("host.docker.internal", "localhost")
        + "/v1/coffee/favourite",
        code=302,
    )


@app.route("/v1/admin/coffee/favourite/leaderboard", methods=["GET", "POST"])
@rate_limiter(
    3,
    60,
    key_prefix="leaderboard",
    getUserId=lambda request: request.headers.get("Authorization"),
)
def proxy_view_leaderboard():
    instance = getInstance()
    return redirect(
        instance.url.replace("host.docker.internal", "localhost")
        + "/v1/admin/coffee/favourite/leaderboard",
        code=302,
    )


@app.route("/v1/<path:subpath>", methods=["GET", "POST"])
def proxy_coffee(subpath):
    if subpath.startswith("coffee/favourite") or subpath.startswith(
        "admin/coffee/favourite/leaderboard"
    ):
        # Skip paths that are handled by other routes
        return
    instance = getInstance()
    return redirect(
        instance.url.replace("host.docker.internal", "localhost") + request.full_path,
        code=302,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
