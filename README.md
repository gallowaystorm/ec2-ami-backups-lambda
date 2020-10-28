# Lambda EC2 Backups Using AMIs

This script automates backups using AMI's that are created based off tags on the EC2 instances.  Currently it is set up to have parameters passed in through CloudWatch.  Those parameters are the Tag value that it's looking for (Daily, Weekly, etc...) and how long the AMIs should live for (in days).
