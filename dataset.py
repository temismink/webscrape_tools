import os
import boto3
from botocore.exceptions import NoCredentialsError

# S3 Client setup
s3 = boto3.client('s3')

# Define bucket and base path
bucket_name = 'deep-fadr'
base_path = 'unzipped/'

def download_from_s3(bucket, s3_key, local_path):
    try:
        # Check if file already exists locally
        if os.path.exists(local_path):
            print(f"File already exists: {local_path}")
            return
        
        if not os.path.exists(os.path.dirname(local_path)):
            os.makedirs(os.path.dirname(local_path))
        
        s3.download_file(bucket, s3_key, local_path)
        print(f"Downloaded: {s3_key}")
    except NoCredentialsError:
        print("Credentials not available")
    except Exception as e:
        print(f"Error downloading {s3_key}: {e}")


VOCAL_PATTERNS = ['LeadVox', 'LeadVocal', 'LeadVoxDT', 'LeadVoxAlt', 'BackingVox', 'BackingVoxDT', 'Vox', 'Vocal']

def is_vocal_track(filename):
    filename_lower = filename.lower()
    for pattern in VOCAL_PATTERNS:
        if pattern.lower() in filename_lower:
            return True
    return False

def download_vocal_tracks():
    continuation_token = None
    while True:
        kwargs = {'Bucket': bucket_name, 'Prefix': base_path}
        if continuation_token:
            kwargs['ContinuationToken'] = continuation_token
        response = s3.list_objects_v2(**kwargs)
        if 'Contents' in response:
            files = response['Contents']
            for file in files:
                file_key = file['Key']
                if file_key.endswith('/') or 'readme' in file_key.lower():
                    continue
                if is_vocal_track(file_key):
                    local_file_path = os.path.join('downloaded/dataset', file_key)
                    download_from_s3(bucket_name, file_key, local_file_path)
        if response.get('IsTruncated'):
            continuation_token = response.get('NextContinuationToken')
        else:
            break

if __name__ == '__main__':
    download_vocal_tracks()