from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from recipes.models import Ingredient, Tag
from .serializers import IngredientSerializer, TagSerializer


class IngredientsViewSet(ReadOnlyModelViewSet):
    """ViewSet for Ingredients [GET, GET-list]."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagsViewSet(ReadOnlyModelViewSet):
    """ViewSet for Tags [GET, GET-list]."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
