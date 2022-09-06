from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly,
                                        SAFE_METHODS)


class IsAdmin(IsAuthenticated):
    def has_permission(self, request, view):
        return (super().has_permission(request, view)
                and (request.user.is_staff
                     or request.user.is_superuser
                     or request.user.role == 'admin'))


class IsAdminOrReadOnly(IsAdmin):
    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or super().has_permission(request, view))


class IsAdminModeratorAuthorOwnedOrReadOnly(IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or (request.user.role == 'admin')
                or (request.user.role == 'moderator')
                or (request.user == obj.author)
                or (request.user.is_staff))
