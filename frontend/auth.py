import os
import boto3
from botocore.exceptions import ClientError

AWS_REGION = os.getenv("AWS_REGION")
COGNITO_CLIENT_ID = os.getenv("COGNITO_CLIENT_ID")
cognito = boto3.client("cognito-idp", region_name=AWS_REGION)

def signup(email, password):
    try:
        cognito.sign_up(
            ClientId=COGNITO_CLIENT_ID,
            Username=email,
            Password=password,
        )
    except ClientError as e:
        error_code = e.response["Error"]["Code"]

        if error_code == "UsernameExistsException":
            raise ValueError("User already exists, try login instead")

        elif error_code == "InvalidParameterException":
            raise ValueError("Invalid signup details")

        else:
            raise RuntimeError("Signup failed. Please try again later.")


def confirm_signup(email, otp):
    try:
        cognito.confirm_sign_up(
            ClientId=COGNITO_CLIENT_ID,
            Username=email,
            ConfirmationCode=otp,
        )

    except ClientError as e:
        error_code = e.response["Error"]["Code"]

        if error_code == "CodeMismatchException":
            raise ValueError("Invalid OTP. Please check and try again.")

        elif error_code == "ExpiredCodeException":
            raise ValueError("OTP has expired. Please request a new one.")

        elif error_code == "UserNotFoundException":
            raise ValueError("User does not exist. Please sign up again.")

        elif error_code == "NotAuthorizedException":
            raise ValueError("User is already confirmed.")

        else:
            print("Confirm signup failed:", e.response["Error"])
            raise RuntimeError("Unable to verify OTP. Please try again later.")

def login(email, password):
    try:
        res = cognito.initiate_auth(
            ClientId=COGNITO_CLIENT_ID,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": email,
                "PASSWORD": password,
            },
        )
        return res["AuthenticationResult"]

    except ClientError as e:
        error_code = e.response["Error"]["Code"]

        if error_code == "NotAuthorizedException":
            # Wrong password OR user not confirmed
            return None

        elif error_code == "UserNotConfirmedException":
            raise ValueError("Please verify your email before logging in.")

        elif error_code == "UserNotFoundException":
            return None

        elif error_code == "TooManyRequestsException":
            raise RuntimeError("Too many login attempts. Please try again later.")

        else:
            print("Login failed:", e.response["Error"])
            raise RuntimeError("Login service is currently unavailable.")
        
def forgot_password(email: str):
    try:
        cognito.forgot_password(
            ClientId=COGNITO_CLIENT_ID,
            Username=email,
        )
        return True

    except ClientError as e:
        error_code = e.response["Error"]["Code"]

        if error_code == "UserNotFoundException":
            raise ValueError("No account found with this email.")

        elif error_code == "LimitExceededException":
            raise RuntimeError("Password reset limit exceeded. Try again later.")

        elif error_code == "TooManyRequestsException":
            raise RuntimeError("Too many requests. Please wait and try again.")

        elif error_code == "InvalidParameterException":
            raise ValueError("Invalid email address.")

        else:
            print("Forgot password failed:", e.response["Error"])
            raise RuntimeError("Unable to process password reset request.")

def confirm_forgot_password(email: str, code: str, new_password: str):
    try:
        cognito.confirm_forgot_password(
            ClientId=COGNITO_CLIENT_ID,
            Username=email,
            ConfirmationCode=code,
            Password=new_password,
        )
        return True

    except ClientError as e:
        error_code = e.response["Error"]["Code"]

        if error_code == "CodeMismatchException":
            raise ValueError("Invalid verification code.")

        elif error_code == "ExpiredCodeException":
            raise ValueError("Verification code has expired.")

        elif error_code == "InvalidPasswordException":
            raise ValueError("Password does not meet security requirements.")

        elif error_code == "UserNotFoundException":
            raise ValueError("User does not exist.")

        elif error_code == "LimitExceededException":
            raise RuntimeError("Too many attempts. Please try again later.")

        else:
            print("Confirm forgot password failed:", e.response["Error"])
            raise RuntimeError("Unable to reset password. Please try again later.")


