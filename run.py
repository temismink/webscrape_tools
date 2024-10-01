import os
import boto3
import zipfile
from io import BytesIO
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the S3 client
s3_client = boto3.client('s3')
bucket_name = 'deep-fadr'
prefix = 'sam/vocal_stems/'

def list_files(bucket_name, prefix=''):
    """List all files in the given S3 bucket."""
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    for obj in response.get('Contents', []):
        yield obj['Key']

def download_zip_file(file_key):
    """Download the entire zip file into memory."""
    s3_response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    return BytesIO(s3_response['Body'].read())

def folder_exists(folder_prefix):
    """Check if a folder already exists in the S3 bucket."""
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_prefix, Delimiter='/')
    return 'Contents' in response

def process_file(file_key):
    """Process a single zip file from S3 using Python's built-in zipfile module."""
    # Extract folder name from file key to check if it already exists
    folder_name = 'unzipped/' + file_key.replace(prefix, '').replace('.zip', '') + '/'
    if folder_exists(folder_name):
        logging.info(f"Skipping entire folder as it already exists: {folder_name}")
        return  # Skip processing if the folder already exists

    try:
        logging.info(f"Starting to process file: {file_key}")
        zip_data = download_zip_file(file_key)
        
        # Use zipfile to read the content of the zip file
        with zipfile.ZipFile(zip_data) as z:
            for file_name in z.namelist():
                s3_key = f'{folder_name}{file_name}'.replace("'", "")
                
                # Read the content of the current file in the zip archive
                with z.open(file_name) as file:
                    s3_client.upload_fileobj(file, bucket_name, s3_key)
                    logging.info(f"File '{file_name}' has been uploaded to S3 bucket '{bucket_name}' with key '{s3_key}'")
    
    except zipfile.BadZipFile:
        logging.error(f"Error processing file {file_key}: Bad zip file.")
    except Exception as e:
        logging.error(f"Unexpected error processing file {file_key}: {str(e)}")

if __name__ == "__main__":
    for file_key in list_files(bucket_name, prefix=prefix):
        if file_key.endswith('.zip'):
            logging.info(f"Processing file: {file_key}")
            process_file(file_key)
