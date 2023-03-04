from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientsViewSet, TagsViewSet

router = DefaultRouter()
router.register("ingredients", IngredientsViewSet, basename="ingredients")
router.register("tags", TagsViewSet, basename="tags")

urlpatterns = [
    path("", include(router.urls)),
]
