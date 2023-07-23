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
website_cooldowns = dict()


async def send_async_request_html(url, params=None, data=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, json=data) as response:
            response_text = await response.text()
            status = response.status
            return response_text, status


async def send_async_request_json(url, params=None, data=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, json=data) as response:
            response_json = await response.json()
            status = response.status
            return response_json, status


@app.route("/ping")
def ping():
    return "I AM OK!", 200


@app.route('/reservePod', methods=['GET'])
async def reserve_pod():
    website = request.json['website']
    if website not in website_cooldowns:
        website_cooldowns[website] = get_cooldown(website)
    cooldown = website_cooldowns[website]
    config.load_incluster_config()  # Если ваше приложение работает внутри кластера Kubernetes

    v1 = client.CoreV1Api()
    pods = v1.list_namespaced_pod(namespace, label_selector="app=chrome-driver-app")
    pod_ips = []
    pods_keys = []
    for pod in pods.items:
        pod_ip = pod.status.pod_ip
        pod_status = pod.status.phase

        if pod_status == "Running":
            response_json, response_code = await send_async_request_json(f"http://{pod_ip}:8082/tryReserve",
                                                                    params={'website': website, 'cooldown': cooldown})
            if response_code == 200:
                pod_ips.append(pod_ip)
                pods_keys.append(response_json['key'])
    return {"pods": pod_ips, "keys": pods_keys, "count": len(pod_ips)}, 200


@app.route('/getPage', methods=['GET'])
async def handle_request():
    logging.info(request.json)
    url = request.json['url']
    website = request.json['website']
    pod_id = request.json['pod_id']
    pod_key = request.json['key']

    logging.info('Send a request')
    t1 = time.time()
    page_source, status = await send_async_request_html(f"http://{pod_id}:8082/getPage",
                                                   data={'url': url, 'website': website, 'key': pod_key})
    logging.info(time.time() - t1)
    return page_source, status


def get_cooldown(website):
    config.load_incluster_config()  # Если ваше приложение работает внутри кластера Kubernetes
    # config.load_kube_config()

    v1 = client.CoreV1Api()
    config_map = v1.read_namespaced_config_map(configmap_name, namespace)

    cooldown_data = config_map.data
    cooldown = cooldown_data.get(website, "0")

    return int(cooldown)


# async def find_available_pod(website, cooldown):
#     config.load_incluster_config()  # Если ваше приложение работает внутри кластера Kubernetes
#     # config.load_kube_config()  # Если ваше приложение работает вне кластера Kubernetes
#
#     v1 = client.CoreV1Api()
#     pods = v1.list_namespaced_pod(namespace, label_selector="app=chrome-driver-app")
#
#     for pod in pods.items:
#         pod_ip = pod.status.pod_ip
#         pod_status = pod.status.phase
#
#         if pod_status == "Running":
#             current_time, _ = await send_async_request(f"http://{pod_ip}:8082/getCooldown", params={'website': website})
#             rand = random.randint(-2, 4)
#             logging.info(current_time)
#             logging.info(cooldown)
#             logging.info(rand)
#             if cooldown + rand - float(current_time) <= 0:
#                 return pod_ip
#
#
#     return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8083)
