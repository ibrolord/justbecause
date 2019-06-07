import boto3
region = 'us-east-1'
instances = ['i-s', 'i-s', 'i-w', 'i-s']

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    sns = boto3.client('sns')
    try:
        ec2.start_instances(InstanceIds=instances) ##stop_instances to stop
        print("Started the instances %s" % (instances))
        sns.publish(
                TopicArn="arn:aws:sns:us-east-1:ACCT:frastructure_Alerts",
                Message="Started the Worker Instances %s" % (instances),
                Subject="Started Worker Instances"
                )
    except Exception as e:
        print("Error:" % e)
        sns.publish(
            TopicArn='arn:aws:sns:us-east-1:ACCT:frastructure_Alerts',
            Message="Starting Instances Failed to Start",
            Subject="Instances failed to start"
            )
