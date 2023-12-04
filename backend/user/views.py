from djoser.views import UserViewSet as UVS
from rest_framework.decorators import action


class DjoserUserCustomView(UVS):
    """Переопределяем джосеровский вьюсет, ограничевая едпоинты и методы."""

    http_method_names = ['get', 'post']

    @action(methods=['GET'], detail=False)
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @action(methods=[''], detail=False)
    def activation(self, request, *args, **kwargs):
        return super().activation(request, *args, **kwargs)

    @action(methods=[''], detail=False)
    def resend_activation(self, request, *args, **kwargs):
        return super().resend_activation(request, *args, **kwargs)

    @action(methods=['POST'], detail=False)
    def set_password(self, request, *args, **kwargs):
        return super().set_password(request, *args, **kwargs)

    @action(methods=[''], detail=False)
    def reset_password(self, request, *args, **kwargs):
        return super().reset_password(request, *args, **kwargs)

    @action(methods=[''], detail=False)
    def reset_password_confirm(self, request, *args, **kwargs):
        return super().reset_password_confirm(request, *args, **kwargs)

    @action(methods=[''], detail=False)
    def set_username(self, request, *args, **kwargs):
        return super().set_username(request, *args, **kwargs)

    @action(methods=[''], detail=False)
    def reset_username(self, request, *args, **kwargs):
        return super().reset_username(request, *args, **kwargs)

    @action(methods=[''], detail=False)
    def reset_username_confirm(self, request, *args, **kwargs):
        return super().reset_username_confirm(request, *args, **kwargs)
