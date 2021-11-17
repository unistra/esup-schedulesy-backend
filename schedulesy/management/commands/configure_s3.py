import pprint

import boto3
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        pp = pprint.PrettyPrinter(indent=4)
        bucket = settings.AWS_STORAGE_BUCKET_NAME
        client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        )

        client.put_bucket_lifecycle_configuration(
            Bucket=bucket,
            LifecycleConfiguration={
                'Rules': [
                    {
                        'Expiration': {
                            'Days': 1,
                        },
                        'ID': 'expiration for the ICS',
                        'Status': 'Enabled',
                        'Prefix': '',
                    },
                ]
            },
        )

        print(f'{bucket} rules :')
        pp.pprint(client.get_bucket_lifecycle_configuration(Bucket=bucket)['Rules'])
