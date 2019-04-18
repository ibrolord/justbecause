import boto3, collections, datetime, time, sys

#Date settings
today = datetime.date.today()
today_string = today.strftime('%Y/%m/%d') #format date
delet_after_days = 10 #delete after 10 days

deletion_date = today - datetime.timedelta(days=delet_after_days) #get difference in days
deletion_date_string = deletion_date.strftime('%Y/%M/%d') #the exact date to delete

ec2 = boto3.client('ec2') #get the EC2 API
regions = ec2.describe_regions().get('Regions',[] ) #get AWS regions
all_regions = [region['RegionName'] for region in regions]

#passing to AWS Lambda
def lambda_handler(event, context): #the python filename ie lambda_handler.py
	#clean slate
	snapshot_counter = 0
	snap_size_counter = 0
	deletion_counter = 0
	deleted_size_counter = 0

#	#loop across all regions
#	for region_name in all_regions:
#		print('Instances in EC2 Region {0}:'.format(region_name))
#		ec2 = boto3.resource('ec2', region_name=region_name)

#	OR SET ONE REGION
	ec2 = boto3.resource('ec2', region_name='ca-central-1')
	
	#get the tag filter 
	instances = ec2.instances.filter(
		Filters=[
			{'Name': 'tag:auto_snapshot', 'Values': ['true']}
			]
		)

	volume_ids = [] #empty bucket to keep the volumes
	
	#loop through the relevant instance
	for i in instances.all():
		for tag in i.tags:	#Get the name of the instance
			if tag['Key'] == 'Name': #find just the name attrib
				name = tag['Value']

	print('Found tagged instances \'{1}\', id: {0}, state: {2}'.format(i.id, name, i.state['Name']))

	vols = i.volumes.all() #Iterate through each instance's volumes
	for v in vols:
		print('{0} is attached to volume {1}, proceeding to snapshot'.format(name, v.id))
		volume_ids.extend(v.id) #add the volumes to the empty dic
		snapshot = v.create_snapshot(
			Description = 'AutoSnapshot of {0}, on volume {1} - Created {2}'.format(name, v.id, today_string),
			)
		snapshot.create_tags(
			Tags = [
				{
					'Key': 'auto_snap',
					'Value': 'true'
				},
				{
					'Key': 'volume',
					'Value': v.id
				},
				{
					'Key': 'CreatedOn',
					'Value': today_string
				},
				{
					'Key': 'New',
					'Value': '{} autosnap'.format(name)
				}
				]
			)
		print('Snapshot Completed')
		snapshot_counter += 1
		snap_size_counter += snapshot.volume_size

		snapshots = ec2.snapshots.filter(
			Filters=[
				{'Name': 'tag:auto_snap', 'Values': ['true']}
			])

		print('Checking for out of date snapshots for instance {0}...'.format(name))
		for snap in snapshots:
			can_delete = False
			for tag in snap.tags:
				if tag['Key'] == 'CreatedOn':
					created_on_string = tag['Value']
				if tag['Key'] == 'auto_snap':
					if tag['Value'] == 'true':
						can_delete = True
				if tag['Key'] == 'Name':
					name = tag['Value']
			created_on = datetime.datetime.strptime(created_on_string, '%Y/%m/%d').date()

			if created_on <= deletion_date and can_delete == True:
				print('Snapshot id {0}, ({1}) from {2} is {3} or more days old... deleting'.format(snap.id, name, created_on, delet_after_days))
				deleted_size_counter += snap.volume_size
				snap.delete()
				deletion_counter += 1

		print('   Made {0} snapshots totalling {1} GB\
        	Deleted {2} snapshots totalling {3} GB'.format(snapshot_counter, snap_size_counter, deletion_counter, deleted_size_counter))
	  	return	
