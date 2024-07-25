from django.contrib import admin
from django.db.models import CharField, TextField
from blog.models import Post, Comment, Category

admin.site.register(Category)

class PostFieldsListFilter(admin.SimpleListFilter):
    title = 'Post Fields'
    parameter_name = 'post_fields'

    def lookups(self, request, model_admin):
        # Возвращает два значения: идентификатор и отображаемый текст
        return [('all', 'Все поля')]

    def queryset(self, request, queryset):
        if self.value() == 'all':
            # Используйте метод only() для включения всех полей модели
            return queryset.only(*[field.name for field in Post._meta.fields if isinstance(field, (CharField, TextField))])


class PostAdmin(admin.ModelAdmin):
    list_display = ('title',
                    'text',
                    'category',
                    'author',
                    'created_at',
                    'updated_at',
                    )
    search_fields = ['title',
                     'text',
                     'created_at',
                     'updated_at']
    list_filter = [PostFieldsListFilter]

admin.site.register(Post, PostAdmin)


class CommentFieldsListFilter(admin.SimpleListFilter):
    title = 'Comment Fields'
    parameter_name = 'comment_fields'

    def lookups(self, request, model_admin):
        # Возвращает два значения: идентификатор и отображаемый текст
        return [('all', 'Все поля')]

    def queryset(self, request, queryset):
        if self.value() == 'all':
            # Используйте метод only() для включения всех полей модели
            return queryset.only(*[field.name for field in Post._meta.fields if isinstance(field, (CharField, TextField))])


class CommentAdmin(admin.ModelAdmin):
    list_display = ('text',
                    'post',
                    'author',
                    'created_at',
                    'updated_at',
                    )
    search_fields = ['text',
                     'created_at',
                     'updated_at']
    list_filter = [CommentFieldsListFilter]

admin.site.register(Comment, CommentAdmin)