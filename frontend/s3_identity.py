import os
import boto3
from botocore.exceptions import ClientError

AWS_REGION = os.getenv("AWS_REGION")
IDENTITY_POOL_ID = os.getenv("IDENTITY_POOL_ID")
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

USER_POOL_PROVIDER = (
    f"cognito-idp.{AWS_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}"
)


def upload_image(id_token, file):
    try:
        identity = boto3.client("cognito-identity", region_name=AWS_REGION)

        identity_resp = identity.get_id(
            IdentityPoolId=IDENTITY_POOL_ID,
            Logins={USER_POOL_PROVIDER: id_token},
        )

        creds = identity.get_credentials_for_identity(
            IdentityId=identity_resp["IdentityId"],
            Logins={USER_POOL_PROVIDER: id_token},
        )

        s3 = boto3.client(
            "s3",
            region_name=AWS_REGION,
            aws_access_key_id=creds["Credentials"]["AccessKeyId"],
            aws_secret_access_key=creds["Credentials"]["SecretKey"],
            aws_session_token=creds["Credentials"]["SessionToken"],
        )

        key = f"profile/{identity_resp['IdentityId']}/profile.jpg"

        s3.upload_fileobj(
            file,
            S3_BUCKET_NAME,
            key,
            ExtraArgs={"ContentType": file.type},
        )

        return key

    except ClientError as e:
        print("Image upload failed:", e.response["Error"]["Message"])
        raise

def get_presigned_image_url(id_token: str) -> str:
    identity = boto3.client("cognito-identity", region_name=AWS_REGION)

    identity_resp = identity.get_id(
        IdentityPoolId=IDENTITY_POOL_ID,
        Logins={USER_POOL_PROVIDER: id_token}
    )

    creds = identity.get_credentials_for_identity(
        IdentityId=identity_resp["IdentityId"],
        Logins={USER_POOL_PROVIDER: id_token}
    )

    s3 = boto3.client(
        "s3",
        region_name=AWS_REGION,
        aws_access_key_id=creds["Credentials"]["AccessKeyId"],
        aws_secret_access_key=creds["Credentials"]["SecretKey"],
        aws_session_token=creds["Credentials"]["SessionToken"],
    )

    key = f"profile/{identity_resp['IdentityId']}/profile.jpg"

    try:
        s3.head_object(
            Bucket=S3_BUCKET_NAME,
            Key=key
        )
    except ClientError as e:
        if e.response["Error"]["Code"] in ("404", "NoSuchKey"):
            raise FileNotFoundError("Profile image does not exist")
        raise

    return s3.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": S3_BUCKET_NAME,
            "Key": key
        },
        ExpiresIn=300
    )
