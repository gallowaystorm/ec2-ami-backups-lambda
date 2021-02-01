import json
import boto3
import datetime
import time

def lambda_handler(event, context):
    ec = boto3.client('ec2')
    
    #get current date
    delete_date = datetime.date.today() 
    #change current date to fit DeleteOn tag format
    delete_fmt = delete_date.strftime('%m-%d-%Y')
    snapshots = []
    
    #get images that have a DeleteOn tag for current date
    images = ec.describe_images(Filters=[
        {
            'Name': 'tag:DeleteOn',
            'Values': [delete_fmt]
        }],Owners=['self'])
    
    #pull snapshot ids into an array
    length_array = len(images['Images'])
    print(str(length_array) + " AMI's need to be deleted")
    increment = 0
    #get list of EBS snapshot ids of volumes attached to images for deletion in snapshots later
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
    #deregister AMI from amazon
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

    
    