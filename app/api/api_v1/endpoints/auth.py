
import json
from datetime import timedelta

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user import UserOut
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import http_except
from app.api.deps import get_current_user, get_session
from app.core.auth import authenticate_user, generate_jwt
from app.core.config import settings
from app.crud.user import get_user_by_id, get_user_by_username

router = APIRouter()


@router.post("/login")
async def user_login(
    data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_session),
):
    if not data.username:
        raise http_except.incorrect_usrnm_passwd
    
    print(data.username)

    user = await get_user_by_username(db, data.username)
    print("user is ",user)
    if not user:
        raise http_except.incorrect_usrnm_passwd

    valid = authenticate_user(db, user, data.password)
    if not valid:
        raise http_except.incorrect_usrnm_passwd

    if user.is_active is False:
        raise http_except.inactive_user

    jwt_client_access_timedelta = timedelta(
        minutes=settings.CRYPTO_JWT_ACESS_TIMEDELTA_MINUTES
    )
    data_to_be_encoded = {
        "email": user.username,
        "type": "acess_token",
    }

    new_jwt_access = generate_jwt(
        data={"sub": json.dumps(data_to_be_encoded)},
        expires_delta=jwt_client_access_timedelta,
    )

    return {"access_token": new_jwt_access, "token_type": "bearer", "is_superadmin":user.is_super_admin}



@router.get("/me", response_model=UserOut)
async def get_user_information(
    db: AsyncSession = Depends(get_session), u=Depends(get_current_user)
):
    user = await get_user_by_id(db, u.id)
    return user

