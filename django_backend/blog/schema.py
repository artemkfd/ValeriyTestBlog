from ninja import ModelSchema, Schema
from blog.models import Post, Comment


class UserIn(Schema):
    username: str
    password: str


class RegistrationSchema(Schema):
    access: str


class PostSchema(ModelSchema):
    class Meta:
        model = Post
        fields = ('title', 'text', 'category', 'author', 'slug', 'created_at', 'updated_at')


class PostCreateSchema(Schema):
    title: str
    text: str
    category_id: int


class CommentSchema(ModelSchema):
    class Meta:
        model = Comment
        fields = ('id', 'text', 'post', 'author', 'created_at', 'updated_at')


class CommentCreateSchema(Schema):
    text: str
    post_id: int


class Confirm(Schema):
    success: bool


class Error(Schema):
    detail: str
