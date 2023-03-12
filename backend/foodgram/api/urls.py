from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    IngredientsViewSet,
    TagsViewSet,
    RecipeViewSet,
    ShoppingCartViewSet,
    FavoriteViewSet,
    SubscriptionViewSet,
)

app_name = "api"

router = DefaultRouter()
router.register("ingredients", IngredientsViewSet, basename="ingredients")
router.register("tags", TagsViewSet, basename="tags")
router.register("recipes", RecipeViewSet, basename="recipes")
router.register(
    r"recipes/(?P<recipe_id>\d+)/shopping_cart",
    ShoppingCartViewSet,
    basename="shopping_cart",
)
router.register(
    r"recipes/(?P<recipe_id>\d+)/favorite",
    FavoriteViewSet,
    basename="favorites",
)
router.register("subscriptions", SubscriptionViewSet, basename="subscriptions")
router.register(
    r"users/(?P<user_id>\d+)/subscribe",
    SubscriptionViewSet,
    basename="subscribe",
)

urlpatterns = [
    path("", include(router.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
