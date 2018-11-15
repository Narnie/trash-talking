# Image recognition service for BenderBin 
# Uses Amazons Rekognition service to identify preset labels from images passed in. 

#!/usr/bin/env python
import boto3
import uuid
import os
import json
from pprint import pprint
from boto3 import client
from os import path

CONFIDENCE = 80
MAX_LABELS = 10
BUCKET = "reaio-trash-talk"
KEY_PREFIX = "images/"
REGION = "ap-southeast-2"

SF = "IMG_3411.JPG"

def copy_to_s3(relFile):
    """ Accepts a relative file path and uploads the file to S3 with a generated key that ends with the 
        last extension on the passed in file
        returns the generated key
    """
    conn = client('s3')

    extention = str(os.path.splitext(os.path.basename(relFile))[1])
    key = KEY_PREFIX + str(uuid.uuid4()) + extention

    localFile = path.relpath(relFile)
    print("Uploading to S3 at " + key + "...")
    with open(localFile, 'rb') as data:
        conn.upload_fileobj(data, BUCKET, key)

    return key

def detect_labels(key):
    """ Accepts a key for and existing S3 object, runs it through Rekognition and returns detected labels
    """
    rekognition = boto3.client("rekognition", REGION)
    print("Rekognising...")
    response = rekognition.detect_labels(
        Image={
            "S3Object": {
                "Bucket": BUCKET,
                "Name": key,
            }
        },
        MaxLabels = MAX_LABELS,
        MinConfidence = CONFIDENCE,
    )
    resultingLabels = list()
    
    for label in response['Labels']:
        resultingLabels.append(label["Name"])

    return resultingLabels

def debug_print():
    """ debugger as an example
    """
    result = detect_labels(copy_to_s3(SF))
    print(result)
    return

# debug_print()