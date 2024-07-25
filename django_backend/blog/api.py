from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_jwt.tokens import RefreshToken

from blog.models import Post, Comment, Category
from ninja_extra import NinjaExtraAPI

from blog.schema import (
    UserIn,
    PostSchema,
    RegistrationSchema,
    Error,
    PostCreateSchema,
    Confirm,
    CommentSchema,
    CommentCreateSchema,
)

api = NinjaExtraAPI()

# Регистрация: пользователь вводит username и password.
# На сервере генерируется токен - строка из 256 рандомных символов.


@api.post("registration/", response={200: RegistrationSchema, 404: Error})
def registration(request, data: UserIn):
    try:
        user = User.objects.create_user(username=data.username, password=data.password)
        refresh = RefreshToken.for_user(user)
    except IntegrityError as ex:
        print(f"Error: {ex}")
        # может лучше скрыть данную ошибку, так как она показывает злоумышленникам,
        # что данный пользователь уже есть в системе
        return 404, {"detail": "IntegrityError"}

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


# Посты. Добавить ендпоинты на просмотр, cоздание, обновление, удалений статей.
# Предусмотреть, что обновлять и удалять пользователь может только свою статью.


@api.get("posts/", response=list[PostSchema], auth=JWTAuth())
def get_all_posts(request):
    return Post.objects.all()


@api.post("posts/", response={201: PostSchema, 404: Error}, auth=JWTAuth())
def create_post(request, post: PostCreateSchema):
    print(request.user)
    if post.category_id:
        category_exists = Category.objects.filter(id=post.category_id).exists()
        if not category_exists:
            return 404, {"detail": "Нет такой категории, измените ID категории"}
    else:
        return 404, {"detail": "Не указана категория"}

    post_model = Post.objects.create(
        title=post.title,
        text=post.text,
        category_id=post.category_id,
        author_id=request.user.id,
    )
    return 201, post_model


@api.put(
    "posts/{post_slug}/edit", response={200: PostSchema, 404: Error}, auth=JWTAuth()
)
def update_post(request, post_slug, data: PostCreateSchema):
    print("data ", data)
    print(request.user)
    post = get_object_or_404(Post, slug=post_slug)
    if post.author != get_object_or_404(User, id=request.user.id):
        return 404, {"detail": "Доступ закрыт. Пост другого автора"}

    is_edited_flag = False
    if post.title != data.title:
        is_edited_flag = True
        post.title = data.title
    if post.text != data.text:
        is_edited_flag = True
        post.text = data.text
    if post.category.id != data.category_id:
        # смена категории поста
        is_edited_flag = True
        new_category = get_object_or_404(Category, id=data.category_id)
        post.category = new_category

    if is_edited_flag:
        post.save()

    return 200, post


@api.delete("posts/{post_slug}", response={200: Confirm, 404: Error}, auth=JWTAuth())
def delete_post(request, post_slug: str):
    print(request.user)
    post = get_object_or_404(Post, slug=post_slug)
    if post.author != get_object_or_404(User, id=request.user.id):
        return 404, {"detail": "Доступ закрыт. Пост другого автора"}
    else:
        post.delete()
        return 200, {"success": True}


# Добавить ендпоинты на просмотр, создание, обновление, удаление комментариев к статье.
# Предусмотреть, что обновлять и удалять пользователь может только cвой комментарий.


@api.get("comments/", response=list[CommentSchema], auth=JWTAuth())
def get_comments(request):
    return Comment.objects.all()


@api.post("comments/", response={201: CommentSchema}, auth=JWTAuth())
def create_comment(request, data: CommentCreateSchema):
    print(request.user)

    # проверяем есть ли такой пост, если нет выдаем ошибку
    get_object_or_404(Post, id=data.post_id)

    comment_model = Comment.objects.create(
        text=data.text, post_id=data.post_id, author_id=request.user.id
    )
    return 201, comment_model


@api.put(
    "comments/{comment_id}/edit",
    response={200: CommentSchema, 404: Error},
    auth=JWTAuth(),
)
def update_comment(request, comment_id, data: CommentCreateSchema):
    print("data ", data)
    print(request.user)

    comment = get_object_or_404(Comment, id=comment_id)

    if comment.author != get_object_or_404(User, id=request.user.id):
        return 404, {"detail": "Доступ закрыт. Комментарий другого автора"}

    is_edited = False
    if comment.text != data.text:
        comment.text = data.text
        is_edited = True

    if comment.post.id != data.post_id:
        # комментарий теперь к другому посту
        new_post = get_object_or_404(Post, id=data.post_id)
        comment.post = new_post
        is_edited = True

    if is_edited:
        comment.save()

    return 200, comment


@api.delete("comments/{comment_id}", response={200: Confirm, 404: Error}, auth=JWTAuth())
def delete_comment(request, comment_id: int):
    print(request.user)
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.author != get_object_or_404(User, id=request.user.id):
        return 404, {"detail": "Доступ закрыт. Комментарий другого автора"}
    else:
        comment.delete()
        return 200, {"success": True}


api.register_controllers(NinjaJWTDefaultController)
