import boto3, collections, datetime, time, sys

#Date settings
today = datetime.date.today()
today_string = today.strftime('%Y/%m/%d') #format date
delet_after_days = 0 #delete after 10 days

deletion_date = today - datetime.timedelta(days=delet_after_days) #get difference in days
deletion_date_string = deletion_date.strftime('%Y/%m/%d') #the exact date to delete
print('today {0} todaystr {1} delet_after_days {2} deletion_date {3} deletion_date_string {4}'.format(today, today_string, delet_after_days, deletion_date, deletion_date_string))
#today 2019-04-18 todaystr 2019/04/18 delet_after_days 1 deletion_date 2019-04-17 deletion_date_string 2019/04/17

##If you want to change profiles from within the code itself, you could just do an export AWS_DEFAULT_PROFILE=
#session = boto3.Session(profile_new=Dev)
#ec2 = session.client('ec2')

ec2 = boto3.client('ec2') #get the EC2 API
#print = <botocore.client.EC2 object at 0x7fb32505c710>

#regions = ec2.describe_regions().get('Regions',[] ) #get AWS regions
#all_regions = [region['RegionName'] for region in regions]

#passing to AWS Lambda
#def lambda_handler(event, context): #the python filename ie lambda_handler.py
#clean slate
snapshot_count = 0
snap_size_count = 0
deletion_count = 0
deleted_size = 0

#	#loop across all regions
#for region_name in all_regions:
#	print('Instances in EC2 Region {0}:'.format(region_name))
#	ec2 = boto3.resource('ec2', region_name=region_name)

#	OR SET ONE REGION
ec2 = boto3.resource('ec2', region_name='us-east-1') ##resources allows you pass high level artributes
#print = ec2.ServiceResource()

#get the tag filter for the instances
instances = ec2.instances.filter(
	Filters=[
		{'Name': 'tag:auto_snapshot', 'Values': ['true']} #look for just instances with this tag
		]
	)
##print = c2.instancesCollection(ec2.ServiceResource(), ec2.Instance)

volume_ids = [] #empty bucket to keep the volumes

#loop through the relevant instance
try:
	for i in instances.all(): #list the instances  print = ec2.instancesCollection(ec2.ServiceResource(), ec2.Instance)
		##print i = ec2.Instance(id='i-068943cf5a8395201')
		for tag in i.tags:	#Get the name of the instance
			##print = {'Key': 'auto_snapshot', 'Value': 'true'}
			if tag['Key'] == 'Name': #find just the name attrib
				name = tag['Value']
				##print = {'Key': 'Name', 'Value': 'geng1'}

		print('Found tagged instances {1}, id: {0}, state: {2}'.format(i.id, name, i.state['Name']))


		#look for volumes to capture and pass volume information for every single volume
		vols = i.volumes.all() #gets all volume infor from the snapshot 
		for v in vols:
		    ##print v = ec2.Volume(id='vol-0fc9cfc3ebeea28c9')
		    print('{0} is attached to vol {1}, proceeding to snap'.format(name, v.id))
		    time.sleep(5)
		    volume_ids.extend(v.id)
		    ##print ec2.Instance.volumesCollection(ec2.Instance(id='i-006113f809ecc11e6'), ec2.Volume)
		    #time.sleep(5)
		    snapshot = v.create_snapshot(
		            Description = 'AutoSnap of {0}, on vol {1} - Created {2}'.format(name, v.id, today_string))
		    ##print ec2.Snapshot(id='snap-0c24443ec2da592e6')
		    #time.sleep(5)
		    snapshot.create_tags(
		    	Tags = [
		    	{
		    		'Key': 'auto_Snap',
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
		    		'Key': 'OCS',
		    		'Value': 'OCS-Weekly-Snapshot'
		    	},
		    	{
		    		'Key': 'Name',
		    		'Value': '{} AutoSnap'.format(name)
		    	}
		    	]
		    	)
		 
		print('snapshot completed')

	snapshot_count += 1
	snap_size_count += snapshot.volume_size ##the ec2.snapshot.volume_size attribute 

	snapshots = ec2.snapshots.filter(
		Filters=[
				{'Name': 'tag:auto_Snap', 'Values': ['true']}
		])

	print('Checking for out of date snapshots for instance {0}'.format(name))
	for snap in snapshots:
		##print(snap, snapshots) = ec2.Snapshot(id='snap-0cf2513371232c911') ec2.snapshotsCollection(ec2.ServiceResource(), ec2.Snapshot)
		can_del = False
		for tag in snap.tags: #get tag of the volume
			##print(tag, snap.tags) ec2.Snapshot(id='snap-0cf2513371232c911') ec2.snapshotsCollection(ec2.ServiceResource(), ec2.Snapshot)
			#Run conditions based off the tags
			if tag['Key'] == 'CreatedOn': #compare the date of the existing snap
					create_onstr = tag['Value']
			if tag['Key'] == 'auto_Snap': #check if it was from one we made 'auto_snap'
				if tag['Value'] == 'true':
					can_del = True #if it was, let python know we can delete
			if tag['Key'] == 'Name': #get the name to make things clean
				name = tag['Value']
		created_on = datetime.datetime.strptime(create_onstr, '%Y/%m/%d').date() #uses the cretion time and formats it in a way we can use

		if created_on <= deletion_date and can_del == True: #if the creation time is less than the deletion time we set with timedelta and it has a can_del (if it was auto_snap)
			print('snapshots id {0}, ({1}) from {2} is {3} or more days old'.format(snap.id, name, created_on, delet_after_days))
			deleted_size += snap.volume_size #+ the new size
			print('Snap size is {0} and deleted_size_counter is {1}'.format(name, deleted_size))
			snap.delete()
			deletion_count += 1

	print('Made {0} snapshots totalling {1} GB Deleted {2} snapshots totalling {3} GB'.format(snapshot_count, snap_size_count, deletion_count, deleted_size))

except Exception as e:
	print(e)
