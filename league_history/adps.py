import os
import requests
from datetime import datetime
import boto3


def get_adp_ppr_fp():
    date = datetime.now()
    s3 = boto3.resource('s3')
    bucket = os.environ.get('S3_BUCKET_NAME')

    res = requests.get('https://www.fantasypros.com/nfl/adp/ppr-overall.php')
    content = res.text

    s3.Bucket(bucket).put_object(Key=f'{date.strftime("%Y%m%d")}_adp_ppr_fp', Body=content)
