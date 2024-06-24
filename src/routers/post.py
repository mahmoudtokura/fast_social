import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from src.database import comments_table, database, post_table
from src.models.post import (
    UserCommentIn,
    UserCommentOut,
    UserPostIn,
    UserPostOut,
    UserPostWithComments,
)
from src.models.user import User
from src.security import get_current_user

router = APIRouter()

logger = logging.getLogger(__name__)


async def find_post(post_id: int):
    logger.info("Finding post by id")
    query = post_table.select().where(post_table.c.id == post_id)
    logger.debug(query)
    return await database.fetch_one(query)


@router.get("/", response_model=list[UserPostOut], status_code=200)
async def read_root():
    logger.info("Getting all posts")
    query = post_table.select()
    logger.debug(query)
    posts = await database.fetch_all(query)
    return [UserPostOut(**post) for post in posts]


@router.post("/post", response_model=UserPostOut, status_code=201)
async def create_post(
    post: UserPostIn, current_user: Annotated[User, Depends(get_current_user)]
):
    logger.info("Creating a post")
    data = {**post.model_dump(), "user_id": current_user.id}
    query = post_table.insert().values(data)
    logger.debug(query)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


@router.get("/post/{post_id}/no-comments", response_model=UserPostOut, status_code=200)
async def read_post(post_id: int):
    logger.info("Getting a post without comments")
    try:
        query = post_table.select().where(post_table.c.id == post_id)
        logger.debug(query)
        record = await database.fetch_one(query)
        return UserPostOut(**record)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Post not found - {e}")


# Comments
@router.post("/comment", response_model=UserCommentOut, status_code=201)
async def create_comment(
    user_comment: UserCommentIn,
    current_user: Annotated[User, Depends(get_current_user)],
):
    logger.info("Add comment to post")

    post = await find_post(user_comment.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    data = {**user_comment.model_dump(), "user_id": current_user.id}
    query = comments_table.insert().values(data)

    logger.debug(query)

    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


@router.get(
    "/post/{post_id}/comment",
    response_model=list[UserCommentOut],
    status_code=200,
)
async def get_comments_on_post(post_id: int):
    logger.info("Get comments on post")
    post = await find_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    query = comments_table.select().where(comments_table.c.post_id == post_id)
    logger.debug(query)
    comment_record = await database.fetch_all(query)
    comments = [
        UserCommentOut(**comment)
        for comment in comment_record
        if comment["post_id"] == post_id
    ]
    return comments


@router.get(
    "/post/{post_id}",
    response_model=UserPostWithComments,
    status_code=200,
)
async def get_post_with_comments(post_id: int):
    logger.info("Get post with comments")
    post = await find_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    comments = await get_comments_on_post(post_id)
    return UserPostWithComments(post=UserPostOut(**post), comments=comments)
