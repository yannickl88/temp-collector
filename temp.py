#!/usr/bin/python

import json
import os
import threading
import time
from datetime import datetime

import persisters
import providers


class Collector(threading.Thread):
    def __init__(self, persister, flush_rate=10):
        threading.Thread.__init__(self)
        self.persister = persister
        self.flush_rate = flush_rate
        self.running = True
        self.lock = threading.Lock()
        self.events = []

    def run(self):
        while self.running:
            try:
                for i in range(self.flush_rate):
                    time.sleep(1)

                self.flush()
            except KeyboardInterrupt:
                self.running = False

    def log(self, path, temp):
        self.lock.acquire()

        timestamp = (datetime.now() - datetime(1970, 1, 1)).total_seconds()
        self.events.append((path, temp, int(timestamp)))

        self.lock.release()

    def flush(self):
        self.lock.acquire()

        if self.persister.persist(self.events):
            del self.events[:]

        self.lock.release()


with open(os.path.dirname(__file__) + os.sep + 'config.json') as config_file:
    config = json.load(config_file)

temp_provider = providers.TemperatureProvider.get(config)
temp_persister = persisters.TemperaturePersister.get(config)

c = Collector(temp_persister, config["flush-rate"])
c.start()

while True:
    c.log(config["metrics"]["path"], temp_provider.temp())

    try:
        for j in range(config["sample-rate"]):
            time.sleep(1)
    except KeyboardInterrupt:
        break

c.join()
