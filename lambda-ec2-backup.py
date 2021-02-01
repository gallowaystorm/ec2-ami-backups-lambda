# Automated AMI Backups
#
# This script will search for all instances having a tag with the name "Backup" and value that is passed in through Cloudwatch
# As soon as we have the instances list, we loop through each instance
# and create an AMI of it. 
#
#Once the image is created we add a DeleteOn tag to the AMI so that it is deleted on a value that is passed in through Cloudwatch
# After creating the AMI it creates a "DeleteOn" tag on the AMI indicating when
# it will be deleted using the DeleteOn tag

import boto3
import collections
import datetime
import sys
import pprint

ec = boto3.client('ec2')

def lambda_handler(event, context):
    #tags passed in through cloudwatch
    backup_on = event['Backup']
    retention = event['DeleteOn']
    #get tag info of instance
    reservations = ec.describe_instances(Filters=[
        {
            'Name': 'tag:Backup',
            'Values': [backup_on]
        },
    ]).get('Reservations', [])

    instances = sum([[i for i in r['Instances']] for r in reservations], [])

    print("Found %d instances that need backing up" % len(instances))

    to_tag = collections.defaultdict(list)

    for instance in instances:
        retention_days = retention
        server_name = ''
        create_time = datetime.datetime.now()
        create_fmt = create_time.strftime('%Y-%m-%d')
        
        for tags in instance['Tags']:
            #set value of server name based off tags
            if tags['Key'] == 'Name':
                server_name = tags['Value']
        #create AMI
        AMIid = ec.create_image(
            InstanceId=instance['InstanceId'],
            Name="Backup - " + server_name + " from " +
            create_fmt,
            Description="Lambda created AMI of instance " +
            instance['InstanceId'] + " from " + create_fmt,
            NoReboot=True,
            DryRun=False)

        pprint.pprint(instance)

        to_tag[retention_days].append(AMIid['ImageId'])

        print("Retaining AMI %s of instance %s for %d days" % (
            AMIid['ImageId'],
            instance['InstanceId'],
            retention_days,
        ))

    print(to_tag.keys())

    for retention_days in to_tag.keys():
        #create value for "DeleteOn" tag
        delete_date = datetime.date.today() + datetime.timedelta(
            days=retention_days)
        delete_fmt = delete_date.strftime('%m-%d-%Y')
        print("Will delete %d AMIs on %s" %
              (len(to_tag[retention_days]), delete_fmt))

        #create DeleteOn tag
        ec.create_tags(Resources=to_tag[retention_days],
                       Tags=[
                           {
                               'Key': 'DeleteOn',
                               'Value': delete_fmt
                           },
                       ])