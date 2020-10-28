import json
import boto3
import datetime

def lambda_handler(event, context):
    ec = boto3.client('ec2')
    
    delete_date = datetime.date.today() 
    delete_fmt = delete_date.strftime('%m-%d-%Y')
    
    images = ec.describe_images(Filters=[
            {
                'Name': 'tag:DeleteOn',
                'Values': [delete_fmt]
            }],Owners=['self'])
    
    for image in images['Images']:
        response = ec.deregister_image(
        ImageId=image['ImageId']
    )