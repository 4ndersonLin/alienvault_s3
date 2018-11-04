import json
import hashlib
import os
import re
import logging
import boto3
from botocore.vendored import requests
from botocore.exceptions import ClientError

# get variable from env
alien_apikey = os.environ['ALIEN_API_KEY']
alien_url = os.environ['ALIEN_URL']
confidence = os.environ['CONFIDENCE']
action_type = os.environ['ACTION']
hook_url = os.environ['HOOK_URL']
slack_channel = os.environ['SLACK_CHANNEL']

# define logger
log_level = os.environ['LOG_LEVEL'].upper()
logger = logging.getLogger()
logger.setLevel(log_level)

detected_pattern = re.compile(r"'alerts': \['Malware infection'\]")

# create s3 high level session
s3 = boto3.resource('s3')

# Do the action we pre-define
def action(detect_count,bucket_name,object_name):
    if int(detect_count) > int(confidence) and action_type == 'DETECTION':
        slack_message = {
            'channel': slack_channel,
            'text': "Detect suspicious file \'%s\' on \'%s\' bucket, please check!" % (object_name,bucket_name)
        }
        response = requests.post(hook_url, data=json.dumps(slack_message), headers={'Content-Type': 'application/json'})
        if response.status_code != 200:
            raise ValueError(
                'Error code is: %s and the response is:\n%s'% (response.status_code, response.text)
            )
        logger.info('push to slack')
    elif int(detect_count) > int(confidence) and action_type == 'PREVENTION':
        obj = s3.Object(bucket_name, object_name)
        buf = obj.delete()
        logger.warning('Delete S3 object: ' + object_name)

# calculator SHA-1 hash
def hash_calculator(b_object):
    hash = hashlib.sha1(b_object).hexdigest()
    logger.info('SHA-1: ' + hash)
    return hash

def lambda_handler(event, context):
    for data in event['Records']:
        bucket_name = data['s3']['bucket']['name']
        object_name = data['s3']['object']['key']
        
        # get object from S3
        obj = s3.Object(bucket_name, object_name)
        buf = obj.get()['Body'].read()
        
        # calculator SHA-1 hash
        h = hash_calculator(buf)
        
        file_url = alien_url + h +'/analysis' 
        headers = {'X-OTX-API-KEY': alien_apikey}
        rsp = requests.get(file_url, headers=headers)
        rsp_json = rsp.text
        rsp_dict = json.loads(rsp_json)
        
        detect_count = 0
        if rsp_dict['analysis'] != None:
            for data in rsp_dict['analysis']['plugins']:
                search = detected_pattern.search(str(rsp_dict['analysis']['plugins'][data]))
                if search:
                    detect_count += 1
                    logger.info('Malware detect by: ' + str(data))
        
        if detect_count > 0:
            action(detect_count,bucket_name,object_name)
        

    return {
        "statusCode": 200,
        "body": json.dumps('Virus scan done!')
    }
