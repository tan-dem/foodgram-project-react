from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientsViewSet, RecipeViewSet, SubscriptionListViewSet,
                    SubscriptionView, TagsViewSet)

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
router.register(
    "users/subscriptions", SubscriptionListViewSet, basename="subscriptions"
)

urlpatterns = [
    path("", include(router.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
    path(
        "users/<int:user_id>/subscribe/",
        SubscriptionView.as_view(),
        name="subscribe"
    ),
]
