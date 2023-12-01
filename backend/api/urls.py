from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    TagViewSet,
    RecipeViewSet,
    IngredientViewSet,
    UserSubscriptionView,
    SubscribeView,
    DjoserUserCustomView,
)

router_v1 = DefaultRouter()

router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')
router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'recipes', RecipeViewSet, basename='recipies')
router_v1.register(r'users', DjoserUserCustomView, basename='djoser-user')
urlpatterns = [
    path(
        'users/subscriptions/',
        UserSubscriptionView.as_view(),
        name='subscriptions'
    ),
    path(
        'users/<int:pk>/subscribe/',
        SubscribeView.as_view(),
        name='subscribe'
    ),
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
