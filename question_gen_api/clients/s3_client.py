import boto3
import os
import io
from dotenv import load_dotenv, find_dotenv
from botocore.exceptions import BotoCoreError, NoCredentialsError
from clients.role_assumer_client import AWSRoleAssumer
from shared.constants import S3_BUCKET_NAME

load_dotenv(find_dotenv())


class AWSS3Client:
    def __init__(self, role_assumer):
        self.role_assumer = role_assumer
        self.s3 = self.create_s3_client()


    def create_s3_client(self):
        credentials = self.role_assumer.get_credentials()
        
        return boto3.client(
            "s3",
            aws_access_key_id=credentials["accessKeyId"],
            aws_secret_access_key=credentials["secretAccessKey"],
            aws_session_token=credentials["sessionToken"],
            region_name=os.getenv("AWS_REGION"),
        )


    def list_folder_objects(self, bucket_name, folder_path):
        self.role_refresh_middleware()
        try:
            response = self.s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_path)
            return [obj["Key"] for obj in response.get("Contents", []) if not obj["Key"].endswith("/")]
        except (BotoCoreError, NoCredentialsError) as e:
            raise RuntimeError(f"Error listing objects: {e}")


    def read_file(self, bucket_name, object_key):
        self.role_refresh_middleware()
        try:
            response = self.s3.get_object(Bucket=bucket_name, Key=object_key)
            return io.BytesIO(response["Body"].read())
        except (BotoCoreError, NoCredentialsError) as e:
            raise RuntimeError(f"Error reading file: {e}")


    def write_file(self, bucket_name, object_key, byte_reader):
        self.role_refresh_middleware()
        try:
            self.s3.put_object(Bucket=bucket_name, Key=object_key, Body=byte_reader)
        except (BotoCoreError, NoCredentialsError) as e:
            raise RuntimeError(f"Error writing file: {e}")


    def role_refresh_middleware(self):
        if self.role_assumer.needs_refresh():
            self.role_assumer.rotate_credentials()
            self.s3 = self.create_s3_client()

if __name__ == '__main__':
    


    role_arn = os.getenv("AWS_ROLE_ARN")
    aws_role_assumer = AWSRoleAssumer(role_arn, rotation_minutes=30)
    s3_client = AWSS3Client(aws_role_assumer)
    bucket_name = S3_BUCKET_NAME
    object_key = ""
    file_output = s3_client.read_file(bucket_name, object_key)
    with open("test.csv", "wb") as f:
        f.write(file_output.read())
