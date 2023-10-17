import logging
import os
import shutil
import time
import cv2
from zipfile import ZipFile
import numpy as np


class ImageLoader:
    def __init__(self, disk):
        self.disk = disk
        self.is_downloading_current_state = False
        self.disk_folder_name = 'temp'
        self.storage_folder = 'images'
        self.image_queue = []

        if os.path.exists(f"{self.disk_folder_name}"):
            shutil.rmtree(f"{self.disk_folder_name}")
        if os.path.exists(f"{self.disk_folder_name}_0"):
            shutil.rmtree(f"{self.disk_folder_name}_0")
        if os.path.exists(f"{self.disk_folder_name}_1"):
            shutil.rmtree(f"{self.disk_folder_name}_1")
        if os.path.exists(f"{self.disk_folder_name}_0.zip"):
            os.remove(f"{self.disk_folder_name}_0.zip")
        os.mkdir(f'{self.disk_folder_name}')

        if self.disk.exists(self.disk_folder_name):
            self.wait_till_progress(self.disk.remove, self.disk_folder_name)
        if self.disk.exists(f'{self.disk_folder_name}_0'):
            self.wait_till_progress(self.disk.remove, f'{self.disk_folder_name}_0')
        if self.disk.exists(f'{self.disk_folder_name}_1'):
            self.wait_till_progress(self.disk.remove, f'{self.disk_folder_name}_1')

        self.disk.mkdir(self.disk_folder_name)

    def wait_till_progress(self, disk_func, *args, **kwargs):
        operation = disk_func(*args, **kwargs, force_async=True)
        while operation.get_status() == 'in-progress':
            time.sleep(0.5)

    def download_current_state(self):
        if not self.is_downloading_current_state:
            self.is_downloading_current_state = True
        else:
            return
        time.sleep(1)

        if os.path.exists(f'{self.disk_folder_name}_0.zip'):
            try:
                with ZipFile(f'{self.disk_folder_name}_0.zip', 'r') as zObject:
                    zObject.extractall(path=f'{self.disk_folder_name}_0')
                files = os.listdir(f'{self.disk_folder_name}_0{os.sep}{self.disk_folder_name}_0')
            except:
                os.remove(f'{self.disk_folder_name}_0.zip')

            for file in files:
                try:
                    shutil.move(f'{self.disk_folder_name}_0{os.sep}{self.disk_folder_name}_0{os.sep}{file}',
                                f'{self.disk_folder_name}{os.sep}{file}')
                    name_parts = file.split('_')
                    platform_name = name_parts[0]
                    offer_id = name_parts[1]
                    i = int(name_parts[2].split('.')[0])
                    self.transform_images((platform_name, i, offer_id))
                except:
                    continue

            shutil.rmtree(f"{self.disk_folder_name}_0")
            os.remove(f'{self.disk_folder_name}_0.zip')

        try:
            if self.disk.exists(f'{self.disk_folder_name}_0'):
                self.disk.download(f'{self.disk_folder_name}_0', f'{self.disk_folder_name}_0.zip')
                self.wait_till_progress(self.disk.rename, f'{self.disk_folder_name}_0', f'{self.disk_folder_name}_1')
                self.wait_till_progress(self.disk.rename, self.disk_folder_name, f'{self.disk_folder_name}_0')
                self.wait_till_progress(self.disk.remove, f'{self.disk_folder_name}_1', permanently=True)
            else:
                self.wait_till_progress(self.disk.rename, self.disk_folder_name, f'{self.disk_folder_name}_0')

            self.disk.mkdir(self.disk_folder_name)
        except:
            if not self.disk.exists(self.disk_folder_name):
                self.disk.mkdir(self.disk_folder_name)
            if self.disk.exists(f'{self.disk_folder_name}_1'):
                self.wait_till_progress(self.disk.remove, f'{self.disk_folder_name}_1', permanently=True)
        self.is_downloading_current_state = False

    def transform_images(self, data):
        platform_name, i, offer_id, = data

        if not os.path.exists(f"{self.storage_folder}/{platform_name}"):
            os.mkdir(f'{self.storage_folder}/{platform_name}')
        if not os.path.exists(f"{self.storage_folder}/{platform_name}/{offer_id}"):
            os.mkdir(f'{self.storage_folder}/{platform_name}/{offer_id}')

        try:
            img = cv2.imread(f'{self.disk_folder_name}/{platform_name}_{offer_id}_{i}.jpg')
            if platform_name == 'avito':
                img = self.cut_image(img)
            resize_img = cv2.resize(img, (256, 256))
            cv2.imwrite(f'{self.storage_folder}/{platform_name}/{offer_id}/image_{i}.jpg', resize_img)
            os.remove(f'{self.disk_folder_name}/{platform_name}_{offer_id}_{i}.jpg')
        except Exception as e:
            print(e, f'{self.disk_folder_name}/{platform_name}_{offer_id}_{i}.jpg')

    def cut_image(self, image):
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        saturation = np.mean(hsv_image, axis=0)
        separate_line = 1
        max_distance_saturation = 0
        max_distance_brightness = 0

        for row in [x for x in range(1, saturation.shape[0]) if
                    x < saturation.shape[0] // 2 - 50 or x > saturation.shape[0] // 2 + 50]:
            if saturation[row, 1] > saturation[row - 1, 1] and saturation[row, 1] - saturation[
                row - 1, 1] >= 1.3 * max_distance_saturation \
                    and saturation[row, 2] < saturation[row - 1, 2] and saturation[row - 1, 2] - saturation[
                row, 2] >= 1.3 * max_distance_brightness:
                separate_line = row
                max_distance_saturation = saturation[row, 1] - saturation[row - 1, 1]
                max_distance_brightness = saturation[row - 1, 2] - saturation[row, 2]

        if separate_line > saturation.shape[0] // 2:
            separate_line = saturation.shape[0] - separate_line

        return image[:, separate_line:-separate_line - 1]


    def load_images_to_disk(self):
        count = 0
        while True:
            if self.is_downloading_current_state:
                time.sleep(5)
                continue
            if len(self.image_queue) > 0:
                data = self.image_queue.pop(0)
                platform_name, offer_id, images_url, i = data['website_name'], data['id'], data['url'], data['index']
                if os.path.exists(f"{self.storage_folder}/{platform_name}/{offer_id}"):
                    continue
                try:
                    self.disk.upload_url(images_url[i], f'{self.disk_folder_name}/{platform_name}_{offer_id}_{i}.jpg', n_retries=5, retry_interval=1)
                    count += 1
                except:
                    time.sleep(5)
                    self.image_queue.append(data)
                    continue
            else:
                time.sleep(2)
            if count >= 100:
                logging.info(f'Количество фоток в очереди: {len(self.image_queue)}')
                count = 0
