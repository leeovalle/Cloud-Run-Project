from google.cloud import storage
from io import BytesIO


storage_client = storage.Client()


def upload_file(bucket_name, blob_name, file_object):  
    """Uploads a file to the bucket."""

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_file(file_object)


def list_files(bucket_name, prefix):
    """Lists all the blobs with the specified prefix in the bucket."""

    blobs = storage_client.list_blobs(bucket_name, prefix=prefix)
    print(blobs)
    list = [blob.name.replace(prefix, "", 1)  for blob in blobs]
    print(list,"success")
    return list



def download_blob(bucket_name, source_blob_name):
    """Downloads a blob from the bucket and returns the content as bytes."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(source_blob_name)
        file_bytes = blob.download_as_bytes()  # Download as bytes
        print(f"Downloaded {len(file_bytes)} bytes") # Log downloaded byte size
        return BytesIO(file_bytes), blob.content_type  # Return BytesIO object

    except Exception as e:
        print(f"Error downloading blob {source_blob_name}: {e}")  # Print the full exception!
        return None, None

