from google.cloud import storage

storage_client = storage.Client()

def get_list_of_files(bucket_name, prefix='images/'): 
    """Lists all the blobs in the bucket with the specified prefix."""
    print("\n")
    print(f"get_list_of_files: {bucket_name}/{prefix}")  
    blobs = storage_client.list_blobs(bucket_name, prefix=prefix) 
    files = []
    for blob in blobs:
        files.append(blob.name.replace(prefix, '', 1)) 
    return files


def upload_file(bucket_name, file_name, prefix='images/'): 
    """Uploads a file to the bucket."""
    print("\n")
    print(f"upload_file: {bucket_name}/{prefix}{file_name}")

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(f"{prefix}{file_name}")  
    blob.upload_from_filename(file_name)
    return


def download_file(bucket_name, file_name, prefix='images/'): 
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(f"{prefix}{file_name}")
    blob.download_to_filename(file_name) 
    blob.reload()