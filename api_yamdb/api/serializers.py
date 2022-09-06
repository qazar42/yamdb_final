from api_yamdb.settings import (CONFORMATION_CODE_MSG_TITLE, DEFAULT_ROLE,
                                EMAIL_HOST_USER
                                )

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Sum
from django.shortcuts import get_object_or_404

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import EmailField

from reviews.models import Category, Comment, Genre, Review, Title, TitleGenre

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    email = EmailField(required=True)

    class Meta:
        model = User
        fields = ('username',
                  'email',
                  'first_name',
                  'last_name',
                  'bio',
                  'role',
                  )

    def validate_role(self, value):
        if value not in ['user', 'admin', 'moderator']:
            raise ValidationError(f'Роль <{value}> некорректна.')
        return value

    def validate_username(self, value):
        if value == 'me':
            raise ValidationError(
                f'Нельзя создать пользователя с именем <{value}>!')
        if User.objects.filter(username=value).exists():
            raise ValidationError(
                f'Пользователь с логином {value} уже существует!')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise ValidationError(
                f'Пользователь с почтой {value} уже существует!')
        return value


class RegistrationSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = ('username',
                  'email',
                  )

    def create(self, validated_data):
        user = User.objects.create(**validated_data,
                                   role=DEFAULT_ROLE)

        confirmation_code = str(user.confirmation_code)
        send_mail(CONFORMATION_CODE_MSG_TITLE, confirmation_code,
                  EMAIL_HOST_USER, [user.email])
        return user


class UserMeSerializer(UserSerializer):
    email = EmailField(required=False)

    class Meta(UserSerializer.Meta):
        read_only_fields = ('username',
                            'email',
                            'role',
                            )


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class DictTitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category', 'rating')

    def get_rating(self, obj):
        queryset_review = obj.reviews.all()
        if queryset_review.count() == 0:
            return None
        score_sum = queryset_review.aggregate(Sum('score'))['score__sum']
        return score_sum // queryset_review.count()


class SlugTitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug', queryset=Genre.objects.all(), many=True)
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all())

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category',)

    def create(self, validated_data):
        genres = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)
        for genre in genres:
            TitleGenre.objects.create(
                title_id=title,
                genre_id=genre
            )
        return title


class ReviewSerializer(serializers.ModelSerializer):
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )
    text = serializers.CharField(
        allow_blank=True,
        required=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Review
        fields = '__all__'

    def validate_score(self, value):
        if value not in range(1, 11):
            raise ValidationError(
                'Оценку можно ставить только в диапазоне от 1 до 10.'
            )
        return value

    def validate(self, data):
        request = self.context['request']
        title_id = self.context['view'].kwargs.get('title_id')
        user = request.user
        title = get_object_or_404(Title, pk=title_id)
        review_exist = Review.objects.filter(title=title, author=user).exists()
        if (
                request.method == 'POST'
                and review_exist
        ):
            raise ValidationError(
                'На одно произведение можно оставить не более одного отзыва.'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.SlugRelatedField(
        slug_field='text',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = '__all__'
