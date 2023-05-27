from kafka import KafkaConsumer
import json
import sys
import os
import argparse
import threading
import time

class LatencyCounter:
    def __init__(self):
        self.message_count = 0
        self.latency_sum = 0

    def process_message(self, device_id, message):
        data = message.value
        print(f"Dispositivo {device_id} recibió datos: {data}")

        receive_time = time.time()
        latency = receive_time - data['timestamp']

        self.message_count += 1
        self.latency_sum += latency

        if self.message_count % 100 == 0:
            average_latency = self.latency_sum / self.message_count
            print(f"Latencia promedio de {self.message_count} mensajes: {average_latency} segundos")

    def consume_data(self, device_id):
        consumer = KafkaConsumer(f'mi_tema_{device_id}', bootstrap_servers='kafka:9092',
                                 value_deserializer=lambda v: json.loads(v.decode('utf-8')), auto_offset_reset='latest')

        for message in consumer:
            self.process_message(device_id, message)

def main(m):
    latency_counter = LatencyCounter()
    threads = []

    for device_id in range(m):
        thread = threading.Thread(target=latency_counter.consume_data, args=(device_id,))
        thread.daemon = True
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', type=int, help='Número de consumidores')
    args = parser.parse_args()

    try:
        main(args.m)
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
