#!/usr/bin/python

import threading
import time
import json

import providers
import persisters


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

        self.events.append((path, temp, int(time.time())))

        self.lock.release()

    def flush(self):
        self.lock.acquire()

        if self.persister.persist(self.events):
            del self.events[:]

        self.lock.release()


with open('config.json') as config_file:
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
