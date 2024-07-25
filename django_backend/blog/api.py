from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_jwt.tokens import RefreshToken

from blog.models import Post, Comment, Category
from ninja_extra import NinjaExtraAPI

from blog.schema import UserIn, PostSchema, RegistrationSchema, Error, PostCreateSchema, Confirm

api = NinjaExtraAPI()

# Регистрация: пользователь вводит username и password.
# На сервере генерируется токен - строка из 256 рандомных символов.


@api.post("registration/", response={200: RegistrationSchema, 202: Error})
def registration(request, data: UserIn):
    try:
        user = User.objects.create(username=data.username, password=data.password)
        refresh = RefreshToken.for_user(user)
        print('refresh -> ', refresh)
    except IntegrityError as ex:
        print(f"Error: {ex}")
        return 202, {'detail': 'IntegrityError'}
    print('refresh.access_token -> ', refresh.access_token)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# Посты. Добавить ендпоинты на просмотр, cоздание, обновление, удалений статей.
# Предусмотреть, что обновлять и удалять пользователь может только свою статью.


@api.get("posts/", response=list[PostSchema], auth=JWTAuth())
def get_all_posts(request):
    return Post.objects.all()


@api.post("posts/", response={200: PostSchema, 404: Error}, auth=JWTAuth())
def create_post(request, post: PostCreateSchema):
    print(request.user)
    if post.category_id:
        category_exists = Category.objects.filter(id=post.category_id).exists()
        if not category_exists:
            return 404, {'detail': 'Нет такой категории, измените ID категории'}
    else:
        return 404, {'detail': 'Не указана категория'}

    post_model = Post.objects.create(title=post.title,
                                     text=post.text,
                                     category_id=post.category_id,
                                     author_id=request.user.id)
    return post_model


@api.put("posts/{post_slug}/edit",
         response={200: PostSchema, 404: Error},
         auth=JWTAuth())
def update_post_data(request, post_slug, data: PostCreateSchema):
    print('data ', data)
    print(request.user)

    post = get_object_or_404(Post, slug=post_slug)
    if post.author != get_object_or_404(User, id=request.user.id):
        return 404, {'detail': 'Доступ закрыт. Пост другого автора'}
    else:
        if post.title != data.title:
            post.title = data.title
        if post.text != data.text:
            post.text = data.text
        if post.category != data.category_id:
            new_category = get_object_or_404(Category, id=data.category_id)
            post.category = new_category
        else:
            return 404, {'detail': 'Нет такой категории'}

        post.save()

    return post


@api.delete("posts/{post_slug}", response={200: Confirm, 404: Error}, auth=JWTAuth())
def delete_post(request, post_slug: str):
    print(request.user)
    post = get_object_or_404(Post, slug=post_slug)
    if post.author != get_object_or_404(User, id=request.user.id):
        return 404, {'detail': 'Доступ закрыт. Пост другого автора'}
    else:
        post.delete()
        return 200, {"success": True}


api.register_controllers(
    NinjaJWTDefaultController
)
