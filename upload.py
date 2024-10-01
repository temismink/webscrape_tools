"""Uploads scraped zip folders to s3"""

import boto3
import requests
from paste import zip_folder_links_list
import os
from tempfile import NamedTemporaryFile
from boto3.s3.transfer import TransferConfig

# Initialize a session using your credentials
session = boto3.Session(
    aws_access_key_id='',
    aws_secret_access_key='',
    region_name='us-east-1'
)

# Create an S3 client
s3 = session.client('s3')

# Configure the multipart upload settings
MB = 1024 ** 2  # one MB
config = TransferConfig(multipart_threshold=100 * MB,  # Set threshold to 100 MB
                        max_concurrency=10,            # Allow up to 10 parts to be uploaded in parallel
                        multipart_chunksize=10 * MB)   # Each part size will be 10 MB

def file_exists_in_s3(bucket_name, object_name):
    """Check if a file already exists in the S3 bucket."""
    try:
        s3.head_object(Bucket=bucket_name, Key=object_name)
        return True  # If head_object doesn't raise an exception, file exists
    except s3.exceptions.ClientError:
        return False  # File doesn't exist

def download_file(url):
    """Download a file from a URL to a temporary file and return the path."""
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        temp_file = NamedTemporaryFile(delete=False)
        for chunk in response.iter_content(chunk_size=8192):
            temp_file.write(chunk)
        temp_file.close()
        return temp_file.name
    else:
        raise Exception(f"Failed to download file from {url}")

def upload_to_s3(url, bucket_name, folder_name):
    try:
        # Determine the final path in the S3 bucket
        object_name = f"{folder_name}/{os.path.basename(url)}"

        # Check if the file already exists in S3
        if file_exists_in_s3(bucket_name, object_name):
            print(f"File {os.path.basename(url)} already exists in {bucket_name}/{folder_name}, skipping upload.")
            return

        # Download the file to a temporary file
        temp_file_path = download_file(url)

        # Upload the file to S3 using multipart settings
        s3.upload_file(temp_file_path, bucket_name, object_name,
                       Config=config)  # Pass the TransferConfig to the upload_file method
        print(f"Uploaded {os.path.basename(url)} to {bucket_name}/{folder_name}")

        # Remove the temporary file
        os.unlink(temp_file_path)
    except Exception as e:
        print(f"Failed to upload {url} to S3: {str(e)}")

# Bucket name where the files will be stored
bucket_name = 'deep-fadr'
folder_name = 'sam/vocal_stems'

# Iterate over all the zip file links and upload them if they are not duplicates
for url in zip_folder_links_list:
    upload_to_s3(url, bucket_name, folder_name)