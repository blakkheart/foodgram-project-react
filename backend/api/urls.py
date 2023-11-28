from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    TagViewSet,
    UserViewSet,
    RecipeViewSet,
    ShoppingCartViewSet,
    FavoriteViewSet,
    IngredientViewSet,
    SubscriptionViewSet,
    shopping_cart_download,
    UserSubscriptionViewSet
)

router_v1 = DefaultRouter()

router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')
router_v1.register(r'tags', TagViewSet, basename='tags')
# router_v1.register(r'users/subscriptions', UserSubscriptionViewSet, basename='users')
# router_v1.register(r'users', UserViewSet, basename='users')
# router_v1.register(r'recipes/download_shopping_cart', ShoppingCartDownloadViewSet, basename='shopping_cart_download')
router_v1.register(r'recipes/(?P<recipes_id>)/shopping_cart', ShoppingCartViewSet, basename='shopping_cart')

# router_v1.register(r'recipes/(?P<recipe_id>\d+)/favorite', FavoriteViewSet, basename='favorite')
# router_v1.register(r'users/subscriptions', SubscriptionViewSet, basename='subscriptionsS')
router_v1.register(r'recipes', RecipeViewSet, basename='recipies')


urlpatterns = [
    path('users/subscriptions/', UserSubscriptionViewSet.as_view()), 
    path('recipes/download_shopping_cart/', shopping_cart_download),
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken')),
]
