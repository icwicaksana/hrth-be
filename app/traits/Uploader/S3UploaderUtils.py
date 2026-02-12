from app.generative.engine import GenAIServices
from botocore.exceptions import ClientError

class S3Uploader:
    def __init__(self, s3_session: None):
        self.s3_session = s3_session or GenAIServices.chatBedrock(return_session=True)
        self.s3_client = self.s3_session.client('s3')
    
    def upload_file(self, file_path, bucket_name, object_name):
        """Uploads a file from a local path to S3."""
        try:
            self.s3_client.upload_file(file_path, bucket_name, object_name)
            return True
        except FileNotFoundError:
            print(f"Error: The file {file_path} was not found.")
            return False
        except ClientError as e:
            print(f"AWS Client Error uploading file: {e}")
            return False

    def download_file(self, bucket_name, object_name, file_path):
        """Downloads a file from S3 to a local path."""
        try:
            self.s3_client.download_file(bucket_name, object_name, file_path)
            return True
        except ClientError as e:
            print(f"AWS Client Error downloading file: {e}")
            return False
            
    def put_objects(self, file_content, bucket_name, object_name):
        """Uploads in-memory content (bytes) to S3."""
        try:
            self.s3_client.put_object(Body=file_content, Bucket=bucket_name, Key=object_name)
            return True
        except ClientError as e:
            print(f"AWS Client Error putting object: {e}")
            return False
            
    def get_object(self, bucket_name, object_name):
        """Gets an object's content (bytes) from S3."""
        try:
            response = self.s3_client.get_object(Bucket=bucket_name, Key=object_name)
            return response['Body'].read()
        except ClientError as e:
            print(f"AWS Client Error getting object: {e}")
            return None

    