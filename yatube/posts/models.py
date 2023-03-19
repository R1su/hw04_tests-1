from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        verbose_name='Заголовок',
        max_length=200
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        unique=True,
        max_length=50
    )
    description = models.TextField(
        verbose_name='Описание группы',
        max_length=200
    )

    def __str__(self):
        return self.title


class Post(models.Model):

    class Meta:
        ordering = ["-pub_date"]

    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    class Meta:
        ordering = ["-created"]

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField(
        verbose_name='Комментарий',
        help_text='Введите текст комментария',
        max_length=200,
    )
    created = models.DateTimeField(
        verbose_name='Дата и время публикации',
        auto_now_add=True,
    )

    def __str__(self):
        return self.text


class Follow(models.Model):
    class Meta:
        unique_together = ('user', 'author')

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )