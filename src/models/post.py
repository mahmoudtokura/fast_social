from pydantic import BaseModel, ConfigDict


class UserPostIn(BaseModel):
    body: str


class UserPostOut(UserPostIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    

class UserCommentIn(BaseModel):
    post_id: int
    body: str


class UserCommentOut(UserCommentIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


class UserPostWithComments(BaseModel):
    post: UserPostOut
    comments: list[UserCommentOut]