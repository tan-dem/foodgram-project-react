from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Favorite, Ingredient, Recipe, ShoppingCart,
                            Subscription, Tag)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from users.models import User

from .filters import IngredientSearchFilter, RecipesFilterSet
from .mixins import CreateDestroyViewSet, ListCreateDestroyViewSet
from .pagination import CustomPageLimitPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (CustomUserCreateSerializer, FavoriteSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          RecipeReadSerializer, SetPasswordSerializer,
                          ShoppingCartSerializer, SubscriptionSerializer,
                          TagSerializer, UserProfileSerializer)


class IngredientsViewSet(ReadOnlyModelViewSet):
    """ViewSet for Ingredients [GET, GET-list]."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (IngredientSearchFilter,)
    search_fields = ("^name",)


class TagsViewSet(ReadOnlyModelViewSet):
    """ViewSet for Tags [GET, GET-list]."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class RecipeViewSet(ModelViewSet):
    """ViewSet for Recipe [GET, GET-list, POST, PATCH, DELETE]."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly | IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPageLimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilterSet

    def get_serializer_class(self):
        if self.action in ("retrieve", "list"):
            return RecipeReadSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @staticmethod
    def post_method_for_actions(request, pk, serializers):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = serializers(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_method_for_actions(request, pk, model):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        model_obj = get_object_or_404(model, user=user, recipe=recipe)
        model_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["POST"],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        return self.post_method_for_actions(
            request=request, pk=pk, serializers=FavoriteSerializer)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_method_for_actions(
            request=request, pk=pk, model=Favorite)

    @action(detail=True, methods=["POST"],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        return self.post_method_for_actions(
            request=request, pk=pk, serializers=ShoppingCartSerializer)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self.delete_method_for_actions(
            request=request, pk=pk, model=ShoppingCart)

    @action(detail=False, methods=["get"])
    def download_shopping_cart(self, request):
        user = request.user

        if not user.shopping_cart.exists():
            return Response(
                {"errors": "Shopping cart is empty"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        text = "Shopping list:\n\n"
        ingredient_name = "recipe__ingredients__name"
        ingredient_unit = "recipe__ingredients__measurement_unit"
        ingredient_qty = "recipe__recipeingredient__amount"
        ingredient_qty_sum = "recipe__recipeingredient__amount__sum"
        shopping_cart = (
            user.shopping_cart.select_related("recipe")
            .values(ingredient_name, ingredient_unit)
            .annotate(Sum(ingredient_qty))
            .order_by(ingredient_name)
        )

        for _ in shopping_cart:
            text += (
                f"{_[ingredient_name]} ({_[ingredient_unit]})"
                f" — {_[ingredient_qty_sum]}\n"
            )
        response = HttpResponse(text, content_type="text/plain")
        filename = "shopping_list.txt"
        response["Content-Disposition"] = f"attachment; filename={filename}"
        return response


# class ShoppingCartViewSet(CreateDestroyViewSet):
#     """ViewSet for ShoppingCart [POST, DELETE]."""
#
#     serializer_class = ShoppingCartSerializer
#
#     def get_queryset(self):
#         return self.request.user.shopping_cart.all()
#
#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         context["recipe_id"] = self.kwargs.get("recipe_id")
#         return context
#
#     def perform_create(self, serializer):
#         serializer.save(
#             user=self.request.user,
#             recipe=get_object_or_404(
#                 Recipe,
#                 id=self.kwargs.get("recipe_id"),
#             ),
#         )
#
#     @action(detail=True, methods=["delete"])
#     def delete(self, request, recipe_id):
#         if (
#             not self.request.user.shopping_cart.select_related("recipe")
#             .filter(recipe_id=recipe_id)
#             .exists()
#         ):
#             return Response(
#                 {"errors": "Recipe is not in shopping cart"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
#         get_object_or_404(
#             ShoppingCart,
#             user=request.user,
#             recipe=recipe_id,
#         ).delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# class FavoriteViewSet(CreateDestroyViewSet):
#     """ViewSet for Favorite [POST, DELETE]."""
#
#     serializer_class = FavoriteSerializer
#
#     def get_queryset(self):
#         return self.request.user.favorites.all()
#
#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         context["recipe_id"] = self.kwargs.get("recipe_id")
#         return context
#
#     def perform_create(self, serializer):
#         serializer.save(
#             user=self.request.user,
#             recipe=get_object_or_404(
#                 Recipe,
#                 id=self.kwargs.get("recipe_id"),
#             ),
#         )
#
#     @action(detail=True, methods=["delete"])
#     def delete(self, request, recipe_id):
#         if (
#             not self.request.user.favorites.select_related("recipe")
#             .filter(recipe_id=recipe_id)
#             .exists()
#         ):
#             return Response(
#                 {"errors": "Recipe is not in favorites"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
#         get_object_or_404(
#             Favorite,
#             user=request.user,
#             recipe=recipe_id,
#         ).delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


class CustomUserViewSet(UserViewSet):
    """ViewSet for User [GET, GET-list, POST]."""

    queryset = User.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPageLimitPagination

    def get_serializer_class(self):
        if self.action == "set_password":
            return SetPasswordSerializer
        if self.action == "create":
            return CustomUserCreateSerializer
        return UserProfileSerializer


class SubscriptionViewSet(ListCreateDestroyViewSet):
    """ViewSet for Subscription [GET-list, POST, DELETE]."""

    serializer_class = SubscriptionSerializer
    pagination_class = CustomPageLimitPagination

    def get_queryset(self):
        return self.request.user.subscriptions.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["author_id"] = self.kwargs.get("user_id")
        return context

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            author=get_object_or_404(User, id=self.kwargs.get("user_id")),
        )

    @action(detail=True, methods=["delete"])
    def delete(self, request, user_id):
        get_object_or_404(User, id=user_id)
        if not Subscription.objects.filter(
            user=request.user, author_id=user_id
        ).exists():
            return Response(
                {"errors": "You were not subscribed to this user"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        get_object_or_404(
            Subscription, user=request.user, author_id=user_id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
