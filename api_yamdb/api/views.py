from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (AllowAny, IsAuthenticated)
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Genre, Review, Title

from .filters import TitleFilter
from .mixins import CreateListDeleteViewset
from .permissions import (IsAdmin, IsAdminModeratorAuthorOwnedOrReadOnly,
                          IsAdminOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          DictTitleSerializer, GenreSerializer,
                          RegistrationSerializer, ReviewSerializer,
                          SlugTitleSerializer, UserMeSerializer, UserSerializer
                          )

User = get_user_model()


@permission_classes([IsAdmin])
class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=username',)
    lookup_field = 'username'
    queryset = User.objects.all()


class GenreViewset(CreateListDeleteViewset):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewset(CreateListDeleteViewset):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TitleViewset(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        dict_var = ['list', 'retrieve']
        if self.action in dict_var:
            return DictTitleSerializer
        return SlugTitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAdminModeratorAuthorOwnedOrReadOnly]

    def get_title(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAdminModeratorAuthorOwnedOrReadOnly]

    def get_review(self):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        return review

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())


@api_view(['PATCH', 'GET'])
@permission_classes([IsAuthenticated])
def user_me_view(request):
    user = request.user
    if request.method == 'GET':
        serializer = UserMeSerializer(instance=user, )
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    serializer = UserMeSerializer(data=request.data, instance=user)
    if serializer.is_valid():
        role = request.data.get('role')
        if (role is not None
                and 'user' == user.role != role):
            json_error = {
                'role': user.role
            }
            return Response(json_error, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.validated_data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny, ])
def register(request):
    serializer = RegistrationSerializer(data=request.data, )
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.validated_data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def token(request):
    username = request.data.get('username')
    confirmation_code = request.data.get('confirmation_code')
    json_err = {}
    if username is None:
        json_err['username'] = 'Имя пользователя не указано!'
    if confirmation_code is None:
        json_err[
            'confirmation_code'] = 'Код подтверждения не указан!'
    if len(json_err) != 0:
        return Response(json_err, status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        json_err = {
            'username': f'Пользователя <{username}> не существует!'
        }
        return Response(json_err, status=status.HTTP_404_NOT_FOUND)
    if str(user.confirmation_code) != confirmation_code:
        json_err = {
            'confirmation_code': 'Код подтверждения не верен!'
        }
        return Response(json_err, status=status.HTTP_400_BAD_REQUEST)
    refresh = RefreshToken.for_user(user)
    json_ans = {
        'token': str(refresh.access_token),
    }
    return Response(json_ans, status=status.HTTP_200_OK)
