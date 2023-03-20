from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CustomUserViewSet,
    IngredientsViewSet,
    RecipeViewSet,
    TagsViewSet,
)

app_name = "api"

router = DefaultRouter()
router.register("ingredients", IngredientsViewSet, basename="ingredients")
router.register("tags", TagsViewSet, basename="tags")
router.register("recipes", RecipeViewSet, basename="recipes")
router.register(
    r"recipes/(?P<recipe_id>\d+)/shopping_cart",
    RecipeViewSet,
    basename="shopping_cart",
)
router.register(
    r"recipes/(?P<recipe_id>\d+)/favorite",
    RecipeViewSet,
    basename="favorites",
)
router.register("users", CustomUserViewSet, basename="users")
router.register(
    r"users/(?P<user_id>\d+)/subscribe",
    CustomUserViewSet,
    basename="subscribe",
)

urlpatterns = [
    path("", include(router.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
