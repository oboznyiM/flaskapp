import requests
from model import Instance
import logging
import app 

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def update_health():
    logger.debug(f"[INSTANCES] Checking instances {app.all_instances}, alive now: {app.alive_instances}")
    for instance in app.all_instances:
        try:
            response = requests.get(f"{instance.url}/health", timeout=1)
            if response.status_code == 200:
                if not instance.is_alive:
                     logger.debug(f"[INSTANCES] Instance {instance.url} is alive again")
                instance.is_alive = True
                if instance not in app.alive_instances:
                    app.alive_instances.append(instance)
            else:
                if instance.is_alive:
                     logger.debug(f"[INSTANCES] Instance {instance.url} died")
                instance.is_alive = False
                if instance in app.alive_instances:
                    app.alive_instances.remove(instance)
        except Exception as e:        
            if instance.is_alive:
                 logger.debug(f"[INSTANCES] Instance {instance.url} died")
            instance.is_alive = False
            if instance in app.alive_instances:
                app.alive_instances.remove(instance)
