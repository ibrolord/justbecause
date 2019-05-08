import boto3, requests
from botocore.client import Config  #You need to import this module becuase of HMAC 4 compatibilty

try:
    s3 = boto3.client('s3', aws_access_key_id='AKIA2D5UXQFTTWI6WUHZ', aws_secret_access_key='a+xa/s', config=Config(signature_version='s3v4', region_name='us-east-1'))
    url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': 'bucket_name',
                'Key': 'aa.tar'
                },
            ExpiresIn='604800' #1 week
            )
    response = requests.get(url)
    print(url, '\n\n',  response)

except Exception as e:
    print(e)
