#!/usr/bin/env python

#compute script for our fib cluster

import pika
import threading,time,sys
import fib_pb2

Q_IP_PATH = "/tmp/data-scale/queue_ip"
#Q_IP_PATH= "localhost"

ip = open(Q_IP_PATH, "r").read()

connection = pika.BlockingConnection(pika.ConnectionParameters(ip))
recvchan = connection.channel()
sendchan = connection.channel()
 
recvchan.queue_declare(queue='fib_to_compute', durable=True)
recvchan.queue_declare(queue='fib_from_compute', durable=True)

def compute_fib(n):
    n_2 = 0
    n_1 = 1

    if(n==0):
        return 0
    elif(n==1):
        return 1

    for i in range(1,n):
        temp = n_2
        n_2 = n_1
        n_1 = n_1 + temp

    return n_1

def recieve_request(ch, method, properties, body):
    print "in recieve"
    ch.basic_ack(delivery_tag = method.delivery_tag)
    try:
        fibList = fib_pb2.FibList()
        fibList.ParseFromString(body)
        for fibInstance in fibList.fibs:
            fibInstance.response = str(compute_fib(fibInstance.n))

        sendchan.basic_publish(exchange='', routing_key='fib_from_compute', 
                               body=fibList.SerializeToString(), 
                               properties=pika.BasicProperties(delivery_mode = 2))
    finally:
        pass

def main():
    
    # let compute forever!!!
    recvchan.basic_qos(prefetch_count=1)
    recvchan.basic_consume(recieve_request, queue='fib_to_compute', no_ack=False)
    recvchan.start_consuming()

main()
