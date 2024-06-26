import logging
import time
import aiohttp
from fastapi import FastAPI, HTTPException, Response
from kubernetes import client, config

logging.basicConfig(level=logging.INFO, format='%(message)s')

app = FastAPI()
namespace = 'default'
configmap_name = "scraper-config"
website_cooldowns = dict()
buffer = dict()


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


@app.get("/ping", status_code=200)
async def ping():
    return "I AM OK!"


@app.get('/reservePod', status_code=200)
async def reserve_pod(request_json: dict):
    website = request_json['website']
    count = request_json['count']
    if count == 'max':
        count = 10000000
    if website not in website_cooldowns:
        website_cooldowns[website] = get_cooldown(website)
    cooldown = website_cooldowns[website]
    config.load_incluster_config()

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
                if count == len(pod_ips):
                    break
    return {"pods": pod_ips, "keys": pods_keys, "count": len(pod_ips)}


@app.get('/getPage', status_code=200)
async def handle_request(request_json: dict):
    logging.info(request_json)
    url = request_json['url']
    website = request_json['website']
    pod_id = request_json['pod_id']
    pod_key = request_json['key']

    logging.info('Send a request')
    t1 = time.time()
    page_source, status = await send_async_request_html(f"http://{pod_id}:8082/getPage",
                                                   data={'url': url, 'website': website, 'key': pod_key})

    if status != 200:
        HTTPException(status_code=status, detail="error inside pod worker")
    logging.info(time.time() - t1)
    headers = {
        "Content-Type": "text/html"
    }
    return Response(content=page_source, headers=headers)


def get_cooldown(website):
    config.load_incluster_config()

    v1 = client.CoreV1Api()
    config_map = v1.read_namespaced_config_map(configmap_name, namespace)

    cooldown_data = config_map.data
    cooldown = cooldown_data.get(f'{website}_cooldown', "0")

    return int(cooldown)

