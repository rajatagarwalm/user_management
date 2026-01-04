from fastapi import (
    FastAPI,
    Depends,
    UploadFile,
    status,
    Query,
)
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from mangum import Mangum

from auth import get_current_user
from dynamodb import (
    save_profile,
    get_profile,
    get_all_profiles,
)
from models import (
    ProfileCreate,
    ProfileUpdate,
    ProfileResponse,
)

import json
from typing import Optional


app = FastAPI()
handler = Mangum(app, lifespan="off")


@app.get("/health")
def health() -> dict:
    print("Health check")
    return {"status": "ok"}


@app.post("/profile/create", response_model=ProfileResponse)
def create_profile(
    data: ProfileCreate,
    user: dict = Depends(get_current_user),
) -> dict:
    save_profile(
        user["sub"],
        user.get("email") or user.get("username"),
        data.dict(),
    )

    return {
        "user_id": user["sub"],
        "email": user.get("email") or user.get("username"),
        **data.dict(),
    }


@app.put("/profile")
def update_profile(
    data: ProfileUpdate,
    user: dict = Depends(get_current_user),
) -> dict:
    save_profile(
        user["sub"],
        user.get("email"),
        data.dict(exclude_none=True),
    )
    return {"message": "Profile updated"}


@app.get("/profile", response_model=ProfileResponse)
def read_profile(
    user: dict = Depends(get_current_user),
) -> ProfileResponse:
    return get_profile(user["sub"])


@app.get("/admin/users")
def admin_users(
    limit: int = Query(10, le=10),
    last_key: Optional[str] = None,
    user: dict = Depends(get_current_user),
):
    if "admin" not in user.get("groups", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin only",
        )

    last_evaluated_key = json.loads(last_key) if last_key else None

    return get_all_profiles(
        limit=limit,
        last_evaluated_key=last_evaluated_key,
    )
