from django.contrib import admin
from .models import Post, Group, Comment

EMPTY_TXT = '-пусто-'


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
        'image',
    )
    list_editable = ('group', 'image', 'author')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = EMPTY_TXT


admin.site.register(Post, PostAdmin)
admin.site.register(Group)
admin.site.register(Comment)