from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    TagViewSet,
    UserViewSet,
    RecipeViewSet,
    IngredientViewSet,
    UserSubscriptionViewSet
)

router_v1 = DefaultRouter()

router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')
router_v1.register(r'tags', TagViewSet, basename='tags')
# router_v1.register(r'users', UserViewSet, basename='users')
# router_v1.register(r'users/subscriptions', SubscriptionViewSet, basename='subscriptionsS')
router_v1.register(r'recipes', RecipeViewSet, basename='recipies')


urlpatterns = [
    path('users/subscriptions/', UserSubscriptionViewSet.as_view(), name='subscriptions'),
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken')),
]
