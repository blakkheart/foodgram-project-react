from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    IngredientViewSet,
    RecipeViewSet,
    SubscribeView,
    TagViewSet,
)


router_v1 = DefaultRouter()

router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')
router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'recipes', RecipeViewSet, basename='recipies')

urlpatterns = [
    path(
        'users/subscriptions/', SubscribeView.as_view(), name='subscriptions'
    ),
    path(
        'users/<int:pk>/subscribe/', SubscribeView.as_view(), name='subscribe'
    ),
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
