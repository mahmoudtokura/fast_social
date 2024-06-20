from fastapi import APIRouter, HTTPException

from src.database import comments_table, database, post_table
from src.models.post import (
    UserCommentIn,
    UserCommentOut,
    UserPostIn,
    UserPostOut,
    UserPostWithComments,
)

router = APIRouter()


async def find_post(post_id: int):
    query = post_table.select().where(post_table.c.id == post_id)
    return await database.fetch_one(query)


@router.get("/", response_model=list[UserPostOut], status_code=200)
async def read_root():
    query = post_table.select()
    posts = await database.fetch_all(query)
    return [UserPostOut(**post) for post in posts]


@router.post("/post", response_model=UserPostOut, status_code=201)
async def create_post(user_post: UserPostIn):
    data = user_post.model_dump()
    query = post_table.insert().values(data)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


@router.get("/post/{post_id}/no-comments", response_model=UserPostOut, status_code=200)
async def read_post(post_id: int):
    try:
        query = post_table.select().where(post_table.c.id == post_id)
        record = await database.fetch_one(query)
        return UserPostOut(**record)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Post not found - {e}")


# Comments
@router.post("/comment", response_model=UserCommentOut, status_code=201)
async def create_comment(user_comment: UserCommentIn):
    post = await find_post(user_comment.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    data = user_comment.model_dump()
    query = comments_table.insert().values(data)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


@router.get(
    "/post/{post_id}/comment",
    response_model=list[UserCommentOut],
    status_code=200,
)
async def get_comments_on_post(post_id: int):
    try:
        post = await find_post(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        query = comments_table.select().where(comments_table.c.post_id == post_id)
        comment_record = await database.fetch_all(query)
        comments = [
            UserCommentOut(**comment)
            for comment in comment_record
            if comment["post_id"] == post_id
        ]
        return comments
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Post not found - {e}")


@router.get(
    "/post/{post_id}",
    response_model=UserPostWithComments,
    status_code=200,
)
async def get_post_with_comments(post_id: int):
    post = await find_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    comments = await get_comments_on_post(post_id)
    return UserPostWithComments(post=UserPostOut(**post), comments=comments)
