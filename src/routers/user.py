import logging

from fastapi import APIRouter, HTTPException, status

from src.database import database, user_table
from src.models.user import UserIn, UserOut
from src.security import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_user,
)

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/register", status_code=201)
async def register_user(user: UserIn):
    if await get_user(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )
    hashed_password = get_password_hash(user.password)
    query = user_table.insert().values(email=user.email, password=hashed_password)
    logger.debug(query)
    await database.execute(query)
    return {"details": "User created"}


@router.get("/users", response_model=list[UserOut], status_code=200)
async def get_users():
    query = user_table.select()
    logger.debug(query)
    users = await database.fetch_all(query)
    return [UserOut(**user) for user in users]


@router.post("/token", response_model=dict, status_code=status.HTTP_200_OK)
async def login(user: UserIn) -> str:
    current_user = await authenticate_user(user.email, user.password)
    access_token = create_access_token(current_user.email)
    return {"access_token": access_token, "token_type": "bearer"}
