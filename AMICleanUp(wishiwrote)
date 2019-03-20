# Automated AMI and Snapshot Deletion
# This code refered with slight changes: https://gist.github.com/bkozora/d4f1cf0e5cf26acdd377
# 
# This script will search for all instances having a tag with "Backup"
# on it. As soon as it has the instances list, it loop through each instance
# and reference the AMIs of that instance. It check that the latest daily backup
# succeeded then it store every image that's reached its DeleteOn tag's date for
# deletion. It then loop through the AMIs, deregister them and remove all the
# snapshots associated with that AMI.

import boto3
import collections
import datetime
import time
import sys

#specify the region in which EC2 Instances located and to cleanup AMI's. Ex: Mumbai region (ap-south-1)
ec = boto3.client('ec2', 'ap-south-1')
ec2 = boto3.resource('ec2', 'ap-south-1')
images = ec2.images.filter(Owners=["XXXXXXXX"])# Specify your AWS account owner id in place of "XXXXX" at all the places in this script

def lambda_handler(event, context):

    reservations = ec.describe_instances(
        Filters=[
            {'Name': 'tag-key', 'Values': ['Backup']},
            { 'Name': 'instance-state-name','Values': ['running'] }
        ]
    ).get(
        'Reservations', []
    )

    instances = sum(
        [
            [i for i in r['Instances']]
            for r in reservations
        ], [])

    print "Found %d instances that need evaluated" % len(instances)

    to_tag = collections.defaultdict(list)

    date = datetime.datetime.now()
    date_fmt = date.strftime('%d-%m-%Y')
    print "Present date and time:" + date.strftime('%d-%m-%Y:%H.%m.%s')
    
    imagesList = []

    # Set to true once we confirm we have a backup taken today
    backupSuccess = False

    # Loop through all of our instances with a tag named "Backup"
    for instance in instances:
	imagecount = 0

        # Loop through each image of our current instance
        for image in images:

            # Our other Lambda Function names its AMIs Lambda - Instance Name.
            # We now know these images are auto created
            if image.name.startswith('Lambda - ' + [result['Value'] for result in instance['Tags'] if result['Key'] == 'Name'][0]):
            #if image.name.startswith('Lambda ec2 tag - ' + [result['Value'] for result in instance['Tags'] if result['Key'] == 'Name'][0]):

                #print "FOUND IMAGE " + image.id + " FOR INSTANCE " + instance['InstanceId']

                # Count this image's occcurance
	        imagecount = imagecount + 1

                try:
                    if image.tags is not None:
                        deletion_date = [
                            t.get('Value') for t in image.tags
                            if t['Key'] == 'DeleteOn'][0]
                        delete_date = time.strptime(deletion_date, "%d-%m-%Y")
        
                except IndexError:
                    deletion_date = False
                    delete_date = False
                
        
                
                today_time = datetime.datetime.now().strftime('%d-%m-%Y')
                # today_fmt = today_time.strftime('%m-%d-%Y')
                today_date = time.strptime(today_time, '%d-%m-%Y')

                
                # If image's DeleteOn date is less than or equal to today,
                # add this image to our list of images to process later
                if delete_date <= today_date:
                    imagesList.append(image.id)
                
                # Make sure we have an AMI from today and mark backupSuccess as true
                if image.name.endswith(date_fmt):
                    
                    # Our latest backup from our other Lambda Function succeeded
                    backupSuccess = True
                    print "Latest backup from " + date_fmt + " was a success"

        print "instance " + instance['InstanceId'] + " has " + str(imagecount) + " AMIs"

    print "============="

    print "About to process the following AMIs:"
    print imagesList

    if backupSuccess == True:
        
        snapshotList = []
        
        for image in imagesList:
            #print image
            desc_image_snapshots = ec.describe_images(ImageIds=[image],Owners=['XXXXXXXX',])['Images'][0]['BlockDeviceMappings']
           # print (desc_image_snapshots)
            try:
                for desc_image_snapshot in desc_image_snapshots:
                    snapshot = ec.describe_snapshots(SnapshotIds=[desc_image_snapshot['Ebs']['SnapshotId'],], OwnerIds=['XXXXXXX'])['Snapshots'][0]
                    #if snapshot['Description'].find(image) > 0:
                    snapshotList.append(snapshot['SnapshotId'])
                    #else:
                    #   continue
                    #     print "Snapshot is not associated with an AMI"
                    
            except Exception as e:
                print "Ignore Index Error:%s" % e.message
                
            print "Deregistering image %s" % image
            amiResponse = ec.deregister_image(
                     DryRun=False,
                   ImageId=image,
                 )

        print "============="
        
        print "About to process the following Snapshots associated with above Images:"
        print (snapshotList)
        
        print "The timer is started for 5 seconds to wait for images to deregister before deleting the snapshots associated to it"    
        time.sleep(5)# This should be set to higher value if the image in the imagesList takes more time to deregister
        
        for snapshot in snapshotList:
            try:
                snap = ec.delete_snapshot(SnapshotId=snapshot)
                print "Deleted snapshot " + snapshot
            
            except Exception as e:
                print "%s" % e.message
        print "-------------"


    else:
        print "No current backup found. Termination suspended."
