import boto, boto.s3, boto.s3.connection
import os, re, sys

def parse_url(url):
    "Extract the components of a URL path for EC2/S3"
    match = re.match("http://(.*?):(\d+)(/(.*$))?", url)
    result = None
    if match and match.groups >= 2:
        host = match.group(1)
        port = int(match.group(2))
        path = match.group(3)
        if path == None:
            path = ""
        result = (host, port, path)
    return result
