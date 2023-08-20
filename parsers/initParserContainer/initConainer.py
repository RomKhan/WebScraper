import sys
from datetime import datetime, timedelta
import os
from kubernetes import client, config

namespace = 'default'
configmap_name = "scraper-config"


def is_exist(type):
    # config.load_kube_config()
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    pods = v1.list_namespaced_pod(namespace, label_selector=f"name=shallow-{type}-parser")
    active_count = 0
    for pod in pods.items:
        start_time = pod.status.start_time
        if pod.status.phase == "Running" and datetime.now(start_time.tzinfo) - start_time > timedelta(minutes=1):
            active_count += 1
    if active_count > 0:
        return True
    return False

def main():
    type = os.environ.get('TYPE')
    # type = 'sale'
    if is_exist(type):
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()