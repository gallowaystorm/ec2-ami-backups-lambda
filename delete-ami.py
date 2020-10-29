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
    ebs_mapping = images['Images'][0]['BlockDeviceMappings']
    print(ebs_mapping)
    for snapshot in ebs_mapping:
        if 'Ebs' in snapshot:
            snapshots.append(snapshot['Ebs']['SnapshotId'])
        else:
            continue
    
    for image in images['Images']:
        print(image)
        response = ec.deregister_image(
        ImageId=image['ImageId']
        )
    #to ensure that the ami is deleted before snapshot is attempting to delete
    time.sleep(10)
        
        #delete snapshots based off snapshot ID array
    for snapshot in snapshots:
        print(snapshot)
        response = ec.delete_snapshot(
            SnapshotId = snapshot
        )
