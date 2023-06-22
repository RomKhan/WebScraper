import os
import time
from csv import DictWriter
import csv
import pandas as pd
import warnings

class DataWorker:
    def __init__(self):
        self.data_to_save_queue = []
        self.is_run = True
        self.keys = set()
        warnings.filterwarnings("ignore")

    def data_dict_flatten(self, data):
        for key in list(data.keys()):
            if type(data[key]) is dict:
                for sub_key in data[key]:
                    data[sub_key] = data[key][sub_key]
                data.pop(key)

    def run(self):
        if os.path.exists('offers.csv'):
            os.remove('offers.csv')
        open('offers.csv', 'w').close()

        while self.is_run:
            if len(self.data_to_save_queue) > 0:
                data = self.data_to_save_queue.pop(0)
                self.data_dict_flatten(data)
                try:
                    df = pd.read_csv('offers.csv')
                except:
                    df = pd.DataFrame()
                df = pd.concat([df, pd.DataFrame([pd.Series(data)])], ignore_index=True)
                df.to_csv('offers.csv', mode='w', index=False)
            else:
                time.sleep(5)



