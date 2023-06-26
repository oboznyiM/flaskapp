from flask import Flask, request, jsonify, redirect
from apscheduler.schedulers.background import BackgroundScheduler
import os
from model import Instance
from health_check import update_health
import requests
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)


all_instances = []
alive_instances = []

scheduler = BackgroundScheduler()
scheduler.add_job(func=update_health, trigger="interval", seconds=15)
scheduler.start()


instances = os.getenv('BACKENDS')
if instances is not None:
    for url in instances.split(','):
        all_instances.append(Instance(url))
    update_health()
current = 0

@app.route('/instances', methods=['POST'])
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

@app.route('/instances', methods=['GET'])
def get_instances():
    return jsonify([{"url": i.url, "isAlive": i.is_alive} for i in all_instances]), 200

@app.route('/v1/<path:subpath>', methods=['GET', 'POST'])
def proxy_coffee(subpath):
    global current
    if len(alive_instances) == 0:
        return jsonify({"error": "No alive instances"}), 503

    current = current % len(alive_instances)
    instance = alive_instances[current]
    current = (current + 1) % len(alive_instances)
    logger.debug(f"[REQUEST] Request redirected to instance {instance.url}")
    return redirect(instance.url.replace("host.docker.internal", "localhost") + request.full_path, code=302)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
