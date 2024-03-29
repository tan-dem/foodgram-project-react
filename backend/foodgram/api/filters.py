from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe
from users.models import User


class IngredientSearchFilter(SearchFilter):
    search_param = "name"


class RecipesFilterSet(FilterSet):
    is_favorited = filters.BooleanFilter(method="filter_is_favorited")
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all(),
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method="filter_is_in_shopping_cart",
    )
    tags = filters.AllValuesMultipleFilter(field_name="tags__slug")

    class Meta:
        model = Recipe
        fields = ["is_favorited", "author", "is_in_shopping_cart", "tags"]

    def filter_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(is_favorited__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(is_in_shopping_cart__user=self.request.user)
        return queryset
