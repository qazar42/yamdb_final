from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import (CategoryViewset, CommentViewSet, GenreViewset,
                    ReviewViewSet, TitleViewset, UserViewSet,
                    register, token, user_me_view)

router_v1 = DefaultRouter()
router_v1.register('users', UserViewSet, basename='user')
router_v1.register('genres', GenreViewset, basename='genre')
router_v1.register('categories', CategoryViewset, basename='category')
router_v1.register('titles', TitleViewset, basename='title')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet, basename='reviews'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

urlpatterns = [
    path('v1/auth/token/', token,
         name='token_obtain_pair'),
    path('v1/auth/signup/', register,
         name='token_verify'),
    path('v1/users/me/', user_me_view, name='users_me'),
    path('v1/', include(router_v1.urls)),
]
