from django.contrib import admin

from .models import Category, Genre, Review, Title, User


@admin.register(Category, Genre, Review, Title, User)
class ReviewAdmin(admin.ModelAdmin):
    pass
