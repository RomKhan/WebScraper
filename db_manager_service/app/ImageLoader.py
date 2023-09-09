import os
import shutil
import time
import cv2
from zipfile import ZipFile


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
        self.is_downloading_current_state = True
        time.sleep(1)
        if self.disk.exists(f'{self.disk_folder_name}_0'):
            self.disk.download(f'{self.disk_folder_name}_0', f'{self.disk_folder_name}_0.zip')
            try:
                self.wait_till_progress(self.disk.rename, f'{self.disk_folder_name}_0', f'{self.disk_folder_name}_1')
            except:
                self.wait_till_progress(self.disk.remove, f'{self.disk_folder_name}_1', permanently=True)

            with ZipFile(f'{self.disk_folder_name}_0.zip', 'r') as zObject:
                zObject.extractall(path=f'{self.disk_folder_name}_0')
            files = os.listdir(f'{self.disk_folder_name}_0{os.sep}{self.disk_folder_name}_0')

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
            self.wait_till_progress(self.disk.rename, self.disk_folder_name, f'{self.disk_folder_name}_0')
            self.wait_till_progress(self.disk.remove, f'{self.disk_folder_name}_1', permanently=True)
        else:
            self.wait_till_progress(self.disk.rename, self.disk_folder_name, f'{self.disk_folder_name}_0')

        self.disk.mkdir(self.disk_folder_name)
        self.is_downloading_current_state = False

    def transform_images(self, data):
        platform_name, i, offer_id, = data

        if not os.path.exists(f"{self.storage_folder}/{platform_name}"):
            os.mkdir(f'{self.storage_folder}/{platform_name}')
        if not os.path.exists(f"{self.storage_folder}/{platform_name}/{offer_id}"):
            os.mkdir(f'{self.storage_folder}/{platform_name}/{offer_id}')

        try:
            img = cv2.imread(f'{self.disk_folder_name}/{platform_name}_{offer_id}_{i}.jpg')
            resize_img = cv2.resize(img, (256, 256))
            cv2.imwrite(f'{self.storage_folder}/{platform_name}/{offer_id}/image_{i}.jpg', resize_img)
            os.remove(f'{self.disk_folder_name}/{platform_name}_{offer_id}_{i}.jpg')
        except Exception as e:
            print(e, f'{self.disk_folder_name}/{platform_name}_{offer_id}_{i}.jpg')


    def load_images_to_disk(self):
        while True:
            if self.is_downloading_current_state:
                time.sleep(5)
                continue
            if len(self.image_queue) > 0:
                data = self.image_queue.pop(0)
                platform_name, offer_id, images_url, i = data['website_name'], data['id'], data['url'], data['index']
                self.disk.upload_url(images_url[i], f'{self.disk_folder_name}/{platform_name}_{offer_id}_{i}.jpg', n_retries=5, retry_interval=1)
            else:
                time.sleep(2)
