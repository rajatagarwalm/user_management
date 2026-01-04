from fastapi import Request, HTTPException, status


def get_current_user(request: Request):
    event = request.scope.get("aws.event")

    if not event:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )

    claims = (
        event
        .get("requestContext", {})
        .get("authorizer", {})
        .get("claims")
    )

    if not claims:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )

    user_id = claims.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user identity"
        )

    groups = claims.get("cognito:groups", [])

    # Normalize groups → always list
    if isinstance(groups, str):
        groups = [groups]
    elif not isinstance(groups, list):
        groups = []

    return {
        "sub": user_id,
        "email": claims.get("email"),
        "username": claims.get("cognito:username"),
        "groups": groups
    }
