from fastapi import Request, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
import requests
import boto3
from botocore.exceptions import ClientError
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

cognito_client = boto3.client(
    "cognito-idp",
    region_name=os.environ["AWS_REGION"]
)

AWS_REGION = os.environ["AWS_REGION"]
USER_POOL_ID = os.environ["COGNITO_USER_POOL_ID"]

ISSUER = f"https://cognito-idp.{AWS_REGION}.amazonaws.com/{USER_POOL_ID}"
JWKS_URL = f"{ISSUER}/.well-known/jwks.json"

jwks = requests.get(JWKS_URL).json()
USER_POOL_CLIENT_ID = os.environ["COGNITO_CLIENT_ID"]

def cognito_signup(email: str, password: str):
    try:
        cognito_client.sign_up(
            ClientId=USER_POOL_CLIENT_ID,
            Username=email,
            Password=password,
        )
        return {"message": "Signup successful. Please confirm OTP."}

    except ClientError as e:
        code = e.response["Error"]["Code"]

        if code == "UsernameExistsException":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists. Please login."
            )

        elif code == "InvalidParameterException":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid signup details."
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Signup failed. Please try again later."
        )

def cognito_confirm_signup(email: str, otp: str):
    try:
        cognito_client.confirm_sign_up(
            ClientId=USER_POOL_CLIENT_ID,
            Username=email,
            ConfirmationCode=otp,
        )
        return {"message": "User confirmed successfully"}

    except ClientError as e:
        code = e.response["Error"]["Code"]

        if code == "CodeMismatchException":
            raise HTTPException(400, "Invalid OTP.")

        elif code == "ExpiredCodeException":
            raise HTTPException(400, "OTP expired.")

        elif code == "UserNotFoundException":
            raise HTTPException(404, "User does not exist.")

        elif code == "NotAuthorizedException":
            raise HTTPException(400, "User already confirmed.")

        raise HTTPException(500, "Unable to verify OTP.")

def cognito_login(email: str, password: str):
    try:
        response = cognito_client.initiate_auth(
            ClientId=USER_POOL_CLIENT_ID,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": email,
                "PASSWORD": password,
            },
        )

        auth = response["AuthenticationResult"]

        return {
            "AccessToken": auth["AccessToken"],
            "IdToken": auth["IdToken"],
            "RefreshToken": auth.get("RefreshToken"),
            "ExpiresIn": auth["ExpiresIn"],
        }

    except ClientError as e:
        code = e.response["Error"]["Code"]

        if code == "NotAuthorizedException":
            raise HTTPException(401, "Invalid email or password.")

        elif code == "UserNotConfirmedException":
            raise HTTPException(403, "Please verify your email.")

        elif code == "UserNotFoundException":
            raise HTTPException(404, "User does not exist.")

        elif code == "TooManyRequestsException":
            raise HTTPException(429, "Too many login attempts.")

        raise HTTPException(500, "Login service unavailable.")

def cognito_forgot_password(email: str):
    try:
        cognito_client.forgot_password(
            ClientId=USER_POOL_CLIENT_ID,
            Username=email,
        )
        return {"message": "OTP sent to registered email."}

    except ClientError as e:
        code = e.response["Error"]["Code"]

        if code == "UserNotFoundException":
            raise HTTPException(404, "User not found.")

        elif code == "LimitExceededException":
            raise HTTPException(429, "Reset limit exceeded.")

        elif code == "TooManyRequestsException":
            raise HTTPException(429, "Too many requests.")

        elif code == "InvalidParameterException":
            raise HTTPException(400, "Invalid email address.")

        raise HTTPException(500, "Unable to process request.")

def cognito_confirm_forgot_password(
    email: str,
    code: str,
    new_password: str,
):
    try:
        cognito_client.confirm_forgot_password(
            ClientId=USER_POOL_CLIENT_ID,
            Username=email,
            ConfirmationCode=code,
            Password=new_password,
        )
        return {"message": "Password reset successful."}

    except ClientError as e:
        err = e.response["Error"]["Code"]

        if err == "CodeMismatchException":
            raise HTTPException(400, "Invalid verification code.")

        elif err == "ExpiredCodeException":
            raise HTTPException(400, "Verification code expired.")

        elif err == "InvalidPasswordException":
            raise HTTPException(400, "Password does not meet policy.")

        elif err == "UserNotFoundException":
            raise HTTPException(404, "User does not exist.")

        elif err == "LimitExceededException":
            raise HTTPException(429, "Too many attempts.")

        raise HTTPException(500, "Unable to reset password.")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header["kid"]

        key = next(
            k for k in jwks["keys"] if k["kid"] == kid
        )

        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)

        claims = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=USER_POOL_CLIENT_ID,
            issuer=ISSUER,
        )

        return {
            "sub": claims["sub"],
            "email": claims.get("email"),
            "username": claims.get("cognito:username"),
            "groups": claims.get("cognito:groups", []),
        }

    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")

    except jwt.InvalidTokenError as e:
        print("JWT ERROR:", str(e))
        raise HTTPException(401, "Invalid token")