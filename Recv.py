import pika
import threading
import json
import requests
import os
import platform

class Recv(object):
    
    def __init__(self, address, queue):
        self.address = address
        self.queue = queue
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.address))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue)

    def create_system_report(self,n):
        """Method to create a system report in JSON.

        Parameters:
        n (str): Report parameter 

        Returns:
        json_data (json): Json object with system info
        """
        data = {}
        data['system'] = platform.system()
        data['architecture'] = platform.architecture()
        data['python_ver'] = platform.python_version()
        data['machine'] = platform.machine()
        data['processor'] = platform.processor()

        json_data = json.dumps(data)

        if str(n) == 'test':
            return platform.system()
        elif str(n) == 'report':
            return json_data
        else:
            return 'Nothing'


    def on_request(self, ch, method, props, body):
        n = body.decode()

        print(" [INFO] Invoke %s" % n)
        response = self.create_system_report(n)

        ch.basic_publish(exchange='',
                        routing_key=props.reply_to,
                        properties=pika.BasicProperties(correlation_id = \
                                                            props.correlation_id),
                        body=str(response))

        ch.basic_ack(delivery_tag = method.delivery_tag)

    def start(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.on_request, queue=self.queue)
        print(" [INFO] Awaiting RPC requests ...")
        self.channel.start_consuming()

if __name__ == '__main__':
    recv_message = Recv('localhost', 'rpc_queue')
    print(recv_message.start())