# Automated AMI Backups
#
# This script will search for all instances having a tag with the name "Backup"
# As soon as we have the instances list, we loop through each instance
# it will use a parameter passed in from Cloudwatch for default value of Backup tag value and retention days.
# After creating the AMI it creates a "DeleteOn" tag on the AMI indicating when
# it will be deleted using the Retention value and another Lambda function

import boto3
import collections
import datetime
import sys
import pprint

ec = boto3.client('ec2')
#image = ec.Image('id')

def lambda_handler(event, context):
    backup_on = event['Backup']
    retention = event['DeleteOn']
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

        #create_image(instance_id, name, description=None, no_reboot=False, block_device_mapping=None, dry_run=False)
        # DryRun, InstanceId, Name, Description, NoReboot, BlockDeviceMappings
        create_time = datetime.datetime.now()
        create_fmt = create_time.strftime('%Y-%m-%d')
        
        for tags in instance['Tags']:
            if tags['Key'] == 'Name':
                server_name = tags['Value']
            
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
        delete_date = datetime.date.today() + datetime.timedelta(
            days=retention_days)
        delete_fmt = delete_date.strftime('%m-%d-%Y')
        print("Will delete %d AMIs on %s" %
              (len(to_tag[retention_days]), delete_fmt))

        #break

        ec.create_tags(Resources=to_tag[retention_days],
                       Tags=[
                           {
                               'Key': 'DeleteOn',
                               'Value': delete_fmt
                           },
                       ])