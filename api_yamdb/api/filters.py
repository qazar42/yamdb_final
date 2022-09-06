from django_filters import (CharFilter, FilterSet, ModelMultipleChoiceFilter,
                            NumberFilter
                            )

from reviews.models import Genre, Title


class TitleFilter(FilterSet):
    genre = ModelMultipleChoiceFilter(
        field_name='genre__slug',
        to_field_name='slug',
        queryset=Genre.objects.all()
    )
    category = CharFilter(field_name='category__slug')
    year = NumberFilter(field_name='year')
    name = CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Title
        fields = ['genre', 'category', 'year', 'name']
