#!/usr/bin/python

import boto.ec2

import os
import re
import sys
import time
import subprocess

import utility

def conn_from_env():

    ec2_access = os.getenv("EC2_ACCESS_KEY")
    ec2_secret = os.getenv("EC2_SECRET_KEY")
    ec2_url = os.getenv("EC2_URL")
    
    ec2_host, ec2_port, ec2_path = utility.parse_url(ec2_url)
    
    region = boto.ec2.regioninfo.RegionInfo()
    region.endpoint = ec2_host
    
    conn = boto.ec2.connection.EC2Connection(
        aws_access_key_id=ec2_access,
        aws_secret_access_key=ec2_secret,
        port=ec2_port,
        path=ec2_path,
        is_secure=False,
        region=region
        )
    
    return conn

def wait_on_instances(instances, poll=5, timeout=10000):

    start_time = time.time()
    end_time = time.time()

    # test the instance to see if it is up
    test = lambda i: i.ip_address != i.private_ip_address

    while((end_time-start_time) < timeout):
        #update all the instances
        map(lambda i: i.update(), instances)

        # check ip addresses
        results = map(test, instances)
        if(all(results)):
            return
        time.sleep(poll)

    raise Exception
    
# creates instances and waits for them to come up.
# returns the reservation associated with these instances
def create_instances(img_id, key, num, conn=None, ud_path=None):
    # if we don't have a conneciton make one
    if(conn == None):
        print "No connection, making a new one"
        conn = conn_from_env()

    print "spinning up instances"
    cloud_init_file = open(ud_path, "r")
    res = conn.run_instances(image_id = img_id, min_count=num, 
                             key_name=key, user_data=cloud_init_file.read())

    print "waiting for instances to come up"
    wait_on_instances(res.instances)

    return res

# writes the user.txt file with commands to create the user.txt file
# with the rabbitmq server's ip address
def write_user_txt(server_ip, outPath):
    fp = open(outPath, "w")
    print >>fp, "#!/bin/bash"
    
    # store the ip address in "queue_ip"
    print >>fp, "echo %s > queue_ip"
    print >>fp, "mkdir /tmp/data-scale"
    print >>fp, "git clone https://github.com/mripley/CloudWork.git"

#compiles the init.txt and user.txt into the combined archive
def compile_user_data(init, user):
    # now the compile init.txt and user.txt into our tar archive
    cmd = "write-mime-multipart --output=combined-userdata.txt user.txt:text/x-shellscript init.txt"
    subprocess.call(cmd, shell=True)

# creates our cloud and waits for it to come up. Returns the connection and 
# reservation  
def create_cloud():
    pass

def main():
    conn = conn_from_env()

    res = create_instances("ami-0000000d", "mripleykey", 1, conn, ud_path="combined-userdata.txt.gz")

    print "instance up and running!"
    time.sleep(10)
    print "terminating instances"

    conn.terminate_instances(res.instances)
main()
