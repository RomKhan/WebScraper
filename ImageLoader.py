import asyncio
import os
import shutil
import threading
import time

import yadisk
import cv2
from zipfile import ZipFile


class ImageLoader:
    def __init__(self, disk):
        self.image_to_disk_queue = []
        self.image_to_local_queue = []
        self.image_to_transform_queue = []
        self.is_run = True
        self.disk = disk
        self.is_downloading_current_state = False
        self.disk_folder_name = 'temp'

    def download_current_state(self):
        is_end = -1
        while self.is_run or is_end > 0:
            time.sleep(50)
            self.is_downloading_current_state = True
            time.sleep(5)

            if self.disk.exists(f'{self.disk_folder_name}_0'):
                self.disk.download(f'{self.disk_folder_name}_0', f'{self.disk_folder_name}_0.zip')
                self.disk.rename(f'{self.disk_folder_name}_0', f'{self.disk_folder_name}_1')

                with ZipFile(f'{self.disk_folder_name}_0.zip', 'r') as zObject:
                    zObject.extractall(path=f'{self.disk_folder_name}_0')
                files = os.listdir(f'{self.disk_folder_name}_0{os.sep}{self.disk_folder_name}_0')

                for file in files:
                    shutil.move(f'{self.disk_folder_name}_0{os.sep}{self.disk_folder_name}_0{os.sep}{file}',
                                f'{self.disk_folder_name}{os.sep}{file}')
                    name_parts = file.split('_')
                    platform_name = name_parts[0]
                    offer_id = name_parts[1]
                    i = int(name_parts[2].split('.')[0])
                    self.image_to_transform_queue.append((platform_name, i, offer_id))
                    # self.disk.remove(f'temp/{file}')

                shutil.rmtree(f"{self.disk_folder_name}_0")
                os.remove(f'{self.disk_folder_name}_0.zip')
                time.sleep(1)
                self.disk.rename(self.disk_folder_name, f'{self.disk_folder_name}_0')
                self.disk.remove(f'{self.disk_folder_name}_1', permanently=True)
                time.sleep(1)
            else:
                self.disk.rename(self.disk_folder_name, f'{self.disk_folder_name}_0')
                time.sleep(1)

            self.disk.mkdir(self.disk_folder_name)
            time.sleep(1)
            self.is_downloading_current_state = False

            if not self.is_run:
                is_end += 1

    def transform_images(self):
        while self.is_run or len(self.image_to_transform_queue) > 0:
            if len(self.image_to_transform_queue) > 0:
                platform_name, i, offer_id, = self.image_to_transform_queue.pop(0)

                if not os.path.exists(f"{platform_name}/{offer_id}"):
                    os.mkdir(f'{platform_name}/{offer_id}')

                try:
                    img = cv2.imread(f'{self.disk_folder_name}/{platform_name}_{offer_id}_{i}.jpg')
                    resize_img = cv2.resize(img, (256, 256))
                    cv2.imwrite(f'{platform_name}/{offer_id}/image_{i}.jpg', resize_img)
                    os.remove(f'{self.disk_folder_name}/{platform_name}_{offer_id}_{i}.jpg')
                except Exception as e:
                    print(e, f'{self.disk_folder_name}/{platform_name}_{offer_id}_{i}.jpg')
            else:
                time.sleep(10)

    def load_images_parallel(self):
        if os.path.exists(f"{self.disk_folder_name}"):
            shutil.rmtree(f"{self.disk_folder_name}")
        if os.path.exists(f"{self.disk_folder_name}_0"):
            shutil.rmtree(f"{self.disk_folder_name}_0")
        if os.path.exists(f"{self.disk_folder_name}_1"):
            shutil.rmtree(f"{self.disk_folder_name}_1")
        if os.path.exists(f"{self.disk_folder_name}_0.zip"):
            os.remove(f"{self.disk_folder_name}_1.zip")
        os.mkdir(f'{self.disk_folder_name}')

        if self.disk.exists(self.disk_folder_name):
            self.disk.remove(self.disk_folder_name)
        if self.disk.exists(f'{self.disk_folder_name}_0'):
            self.disk.remove(f'{self.disk_folder_name}_0')
        if self.disk.exists(f'{self.disk_folder_name}_1'):
            self.disk.remove(f'{self.disk_folder_name}_1')
        time.sleep(15)
        self.disk.mkdir(self.disk_folder_name)

        thread1 = threading.Thread(target=self.download_current_state)
        thread2 = threading.Thread(target=self.transform_images)
        thread1.start()
        thread2.start()

        while self.is_run:
            if len(self.image_to_disk_queue) > 0:
                data = self.image_to_disk_queue.pop(0)
                self.load_images_to_disk(data)

        thread1.join()
        thread2.join()
        os.remove(f'{self.disk_folder_name}')
        self.disk.remove(self.disk_folder_name)

    def load_images_to_disk(self, data):
        platform_name, offer_id, images_url = data[0], data[1], data[2]
        for i in range(len(images_url)):
            if self.is_downloading_current_state:
                time.sleep(5)
                continue
            self.disk.upload_url(images_url[i], f'{self.disk_folder_name}/{platform_name}_{offer_id}_{i}.jpg')
