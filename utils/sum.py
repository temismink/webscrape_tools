import boto3

# Initialize a session using your credentials
session = boto3.Session(
    aws_access_key_id={'secret_id'},
    aws_secret_access_key={'secret_access_key'},
    region_name='us-east-1'
)

# Create an S3 client
s3 = session.client('s3')

def count_folders_in_s3(bucket_name, folder_name):
    """Count the total number of folders (prefixes) in a given S3 bucket."""
    folder_count = 0

    # List objects and common prefixes (folders)
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket_name, Prefix=folder_name, Delimiter='/')

    for page in pages:
        # Check for 'CommonPrefixes', which represent folders
        if 'CommonPrefixes' in page:
            folder_count += len(page['CommonPrefixes'])

    return folder_count

# Bucket and folder name
bucket_name = 'deep-fadr'
folder_name = 'unzipped/'

# Calculate the total number of folders
total_folders = count_folders_in_s3(bucket_name, folder_name)
print(f"Total number of folders in {folder_name} in bucket {bucket_name}: {total_folders}")
