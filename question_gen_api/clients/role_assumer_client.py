import boto3
import time
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)


class AWSRoleAssumer:
    def __init__(self, role_arn: str, rotation_minutes: int):
        self._role_arn = role_arn
        self._rotation_minutes = rotation_minutes
        self._last_rotation_time = datetime.now()
        self._access_key_id = ""
        self._secret_access_key = ""
        self._session_token = ""
        
        self.rotate_credentials()


    def get_credentials(self):
        if self.needs_refresh():
            self.rotate_credentials()
        return {
            "accessKeyId": self._access_key_id,
            "secretAccessKey": self._secret_access_key,
            "sessionToken": self._session_token,
        }


    def rotate_credentials(self):
        sts_client = boto3.client("sts")
        
        try:
            response = sts_client.assume_role(
                RoleArn=self._role_arn,
                RoleSessionName="session"
            )

            
            credentials = response["Credentials"]
            self._access_key_id = credentials["AccessKeyId"]
            self._secret_access_key = credentials["SecretAccessKey"]
            self._session_token = credentials["SessionToken"]
            self._last_rotation_time = datetime.now()
 
        
        except Exception as e:
            raise RuntimeError(f"Unable to assume role: {e}")


    def needs_refresh(self):
        return (datetime.now() - self._last_rotation_time) >= timedelta(minutes=self._rotation_minutes)


if __name__ == '__main__':
    from dotenv import load_dotenv, find_dotenv
    import os
    load_dotenv(find_dotenv())

    role_arn = os.getenv("AWS_ROLE_ARN")
    aws_role_assumer = AWSRoleAssumer(role_arn, rotation_minutes=30)
