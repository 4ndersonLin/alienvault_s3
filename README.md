# Secure your S3 bucket using Alienvault
Hunting malware in your s3 bucket by using Alienvault threat intelligence source.
Have prevention and detection mode.

# Diagram
![Diagram](images/Diagram.png)

# How to use?
## 1. Create an Alienvault account.
Sign up an Alienvault account then go to "https://otx.alienvault.com/api" and get api key.
(Alienvault OTX: https://www.alienvault.com/open-threat-exchange)

## 2. Setup slack webhook(Optional, if you want to use "DETECTION" mode)
Follow 'https://api.slack.com/incoming-webhooks' to the 'Getting started with Incoming Webhooks' section's step 3.
Let your channel and webhook URL ready.

## 3. Create IAM role and Lambda
Creat an IAM role for lambda use and the IAM policy are shown as below.
IAM policy:
* Lambda basic execution permission
* s3:getObject
* s3:putObject

Create Lambda function then setting the enviroment variables.
Lambda's enviroment variables:
* ALIEN_API_KEY: value is your Alienvault api key.
* ALIEN_URL: 'https://otx.alienvault.com/api/v1/indicators/file/'
* ACTION: 'DETECTION' or 'PREVENTION'
* CONFIDENCE: Recommended value is '0', means any source detect this file is malware the lambda do the action(notify or remove).
* HOOK_URL: your slack webhook URL(Necessary when ACTION is DETECTION)
* SLACK_CHANNEL: your slack channel(Necessary when ACTION is DETECTION)
* LOG_LEVEL: lambda log level(Recommended value is 'info')
* TAG: Recommended value is 'TRUE'(Necessary when ACTION is DETECTION)

## 4. Setup S3 event trigger
Follow 'https://docs.aws.amazon.com/AmazonS3/latest/dev/NotificationHowTo.html' and trigger the lambda function we create.

# Quick start using cloudformation.
[![Diagram](images/cfn.png)](https://ap-northeast-1.console.aws.amazon.com/cloudformation/home?region=ap-northeast-1#/stacks/create/review?templateURL=https://s3-ap-northeast-1.amazonaws.com/s3sec-4nderson/packaged.yml)

# Quick start using SAM(severless application model).
Use the sam folder to deploy.
