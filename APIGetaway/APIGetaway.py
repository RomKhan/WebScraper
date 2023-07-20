import asyncio
import logging
import random
import time

import aiohttp
from flask import Flask, request
from kubernetes import client, config

logging.basicConfig(level=logging.INFO, format='%(message)s')

app = Flask(__name__)
namespace = 'default'
configmap_name = "cooldown-config"

async def send_async_request(url, params=None, data=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, json=data) as response:
            response_text = await response.text()
            return response_text


@app.route('/getPage', methods=['GET'])
async def handle_request():
    logging.info(request.json)
    url = request.json['url']
    website = request.json['website']

    cooldown = get_cooldown(website)

    if cooldown > 0:
        # Поиск другого доступного пода без кулдауна
        target_pod = await find_available_pod(website, cooldown)

        if target_pod is not None:
            logging.info('Send a request')
            t1 = time.time()
            page_source = await send_async_request(f"http://{target_pod}:8082/getPage", data={'url': url, 'website': website})
            logging.info(time.time() - t1)
            return page_source
        else:
            return {'message': 'No available pod found'}, 503

    return 'cooldown==0 error'


def get_cooldown(website):
    config.load_incluster_config()  # Если ваше приложение работает внутри кластера Kubernetes
    #config.load_kube_config()

    v1 = client.CoreV1Api()
    config_map = v1.read_namespaced_config_map(configmap_name, namespace)

    cooldown_data = config_map.data
    cooldown = cooldown_data.get(website, "0")

    return int(cooldown)


async def find_available_pod(website, cooldown):
    config.load_incluster_config()  # Если ваше приложение работает внутри кластера Kubernetes
    #config.load_kube_config()  # Если ваше приложение работает вне кластера Kubernetes

    v1 = client.CoreV1Api()
    pods = v1.list_namespaced_pod(namespace, label_selector="app=chrome-driver-app")

    count = 0
    while True and count < 20:
        count += 1
        for pod in pods.items:
            pod_ip = pod.status.pod_ip
            pod_status = pod.status.phase

            if pod_status == "Running":
                current_time = await send_async_request(f"http://{pod_ip}:8082/getCooldown", params={'website': website})
                rand = random.randint(-2, 4)
                logging.info(current_time)
                logging.info(cooldown)
                logging.info(rand)
                if cooldown + rand - float(current_time) <= 0:
                    return pod_ip
            await asyncio.sleep(1)

    return None


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8083)