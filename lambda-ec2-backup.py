# Automated AMI Backups
#
# This script will search for all instances having a tag with the name "Backup"
# As soon as we have the instances list, we loop through each instance
# it will use a parameter passed in from Cloudwatch for default value of Backup tag value and retention days.
# After creating the AMI it creates a "DeleteOn" tag on the AMI indicating when
# it will be deleted using the Retention value and another Lambda function

import json
import boto3
import datetime
import time

def lambda_handler(event, context):
    ec = boto3.client('ec2')
    
    delete_date = datetime.date.today() 
    delete_fmt = delete_date.strftime('%m-%d-%Y')
    snapshots = []
    
    
    images = ec.describe_images(Filters=[
        {
            'Name': 'tag:DeleteOn',
            'Values': [delete_fmt]
        }],Owners=['self'])
    
    #pull snapshot ids into an array
    length_array = len(images['Images'])
    print(str(length_array) + " AMI's need to be deleted")
    increment = 0
    while increment < length_array:
        ebs_mapping = images['Images'][increment]['BlockDeviceMappings']
        print(ebs_mapping)
        for snapshot in ebs_mapping:
            if 'Ebs' in snapshot:
                snapshots.append(snapshot['Ebs']['SnapshotId'])
                print(snapshots)
            else:
                continue
        increment += 1
    
    for image in images['Images']:
        print(image)
        response = ec.deregister_image(
        ImageId=image['ImageId']
        )
    time.sleep(10)
       
        #delete snapshots based off snapshot ID array
    for snapshot in snapshots:
        print(snapshot)
        response = ec.delete_snapshot(
            SnapshotId = snapshot
        )
        print(snapshot + "has been deleted")