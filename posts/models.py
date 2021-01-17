from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='название группы',
        help_text='введите название группы',
    )
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title

class Post(models.Model):
    text = models.TextField(
        max_length=2000,
        verbose_name='текст',
        help_text='Введите текст новой записи',
    )
    pub_date = models.DateTimeField(
        "date published",
        auto_now_add=True,
        db_index=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name="post",
        blank=True,
        null=True,
        verbose_name='группа',
    )

    image = models.ImageField(
        upload_to='media/', 
        blank=True, null=True
    )  


    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text

class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name='Пост',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField(
        max_length=2000,
        verbose_name='текст',
    )
    created = models.DateTimeField(
        "date published",
        auto_now_add=True
    )

class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        null = True,
        on_delete=models.CASCADE,
        related_name='following',
    )