import uuid
from datetime import date

from api_yamdb.settings import DEFAULT_ROLE

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import (CharField, CheckConstraint, Q, TextField,
                              UniqueConstraint)


class User(AbstractUser):
    role = CharField(
        'Роль',
        max_length=10,
        blank=False,
        default=DEFAULT_ROLE
    )
    bio = TextField(
        'Биография',
        blank=True,
    )
    confirmation_code = models.UUIDField('Код подтверждения',
                                         default=uuid.uuid4)


class Genre(models.Model):
    name = models.CharField('Название жанра', max_length=256)
    slug = models.SlugField('Уникальное имя', unique=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField('Название категории', max_length=256)
    slug = models.SlugField('Уникальное имя', unique=True)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.TextField('Название произведения')
    year = models.SmallIntegerField('Год выхода')
    description = models.TextField(
        'Описание произведения',
        max_length=256,
        blank=True)
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр',
        related_name='assigned_genre',
        through='TitleGenre')
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='titles'
    )

    class Meta:
        constraints = (
            CheckConstraint(
                check=(Q(year__lte=date.today().year)),
                name='year_less_today'
            ),
        )
        indexes = [
            models.Index(fields=('year',))
        ]

    def __str__(self):
        return self.name[:15]


class TitleGenre(models.Model):
    title_id = models.ForeignKey(
        Title,
        verbose_name='Идентификатор произведения',
        on_delete=models.CASCADE
    )
    genre_id = models.ForeignKey(
        Genre,
        verbose_name='Идентификатор жанра',
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = (
            UniqueConstraint(
                fields=('title_id', 'genre_id'),
                name='genre_title_unique'
            ),
        )


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.TextField(
        verbose_name='Текст',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )
    score = models.IntegerField(
        validators=[
            MinValueValidator(1, 'Integer value from 1 to 10'),
            MaxValueValidator(10, 'Integer value from 1 to 10')
        ],
        verbose_name='Оценка'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ('-pub_date',)
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'title',),
                name='unique review'
            ),
        )
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'


class Comment(models.Model):
    text = models.TextField(
        verbose_name='Текст',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        ordering = ('-pub_date',)
