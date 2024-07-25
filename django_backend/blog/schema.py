from ninja import ModelSchema, Schema

from blog.models import Post


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


class Confirm(Schema):
    success: bool


class Error(Schema):
    detail: str
