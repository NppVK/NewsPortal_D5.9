from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.functions import Coalesce


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Имя автора')
    rating = models.IntegerField(default=0)

    def update_rating(self):
        posts_rating = Post.objects.filter(author=self).aggregate(pr=Coalesce(Sum('rating'), 0))['pr']
        comments_rating = Comment.objects.filter(user=self.user).aggregate(cr=Coalesce(Sum('rating'), 0))['cr']
        posts_comments_rating = Comment.objects.filter(post__author=self).aggregate(pcr=Coalesce(Sum('rating'), 0))[
            'pcr']
        self.rating = posts_rating * 3 + comments_rating + posts_comments_rating
        self.save()


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='Категории новостей/статей')


class Post(models.Model):
    article = 'A'
    news = 'N'
    TYPES = [
        (article, 'Статья'),
        (news, "Новость")
    ]
    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name="Автор поста")
    post_type = models.CharField(max_length=1, choices=TYPES, default=article, verbose_name="Вид поста")
    datetime = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время создания")
    category = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=255, verbose_name="Заголовок статьи/новости")
    post_text = models.TextField(verbose_name="Текст статьи/новости")
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return f"{self.post_text[:124]}..."


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name="Пост")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    comment_text = models.TextField(verbose_name="Текст комментария")
    datetime = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время создания")
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()
