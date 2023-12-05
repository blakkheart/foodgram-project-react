from rest_framework import permissions


class DjoserMePermission(permissions.BasePermission):
    '''Кастомный пермишен для просмотра эндопинта пользователей.'''

    def has_permission(self, request, view):
        if (
            request.get_full_path() == '/api/users/me/'
            and not request.user.is_authenticated
        ):
            return False
        return True


class RecipePermissions(permissions.BasePermission):
    '''Пермишен для рецептов'''

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user == obj.author
