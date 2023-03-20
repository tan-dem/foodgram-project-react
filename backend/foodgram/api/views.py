from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart,
    Subscription,
    Tag,
)
from users.models import User
from .filters import IngredientSearchFilter, RecipesFilterSet
from .pagination import CustomPageLimitPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    CustomUserCreateSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeReadSerializer,
    SetPasswordSerializer,
    ShoppingCartSerializer,
    SubscriptionCreateSerializer,
    SubscriptionSerializer,
    TagSerializer,
    UserProfileSerializer,
)
from .services import generate_shopping_list


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

    queryset = Recipe.objects.all().order_by("-id")
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
        data = {"user": request.user.id, "recipe": pk}
        serializer = serializers(data=data, context={"request": request})
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

    @action(
        detail=True, methods=["POST"], permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        return self.post_method_for_actions(
            request=request, pk=pk, serializers=FavoriteSerializer
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_method_for_actions(
            request=request, pk=pk, model=Favorite
        )

    @action(
        detail=True, methods=["POST"], permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        return self.post_method_for_actions(
            request=request, pk=pk, serializers=ShoppingCartSerializer
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self.delete_method_for_actions(
            request=request, pk=pk, model=ShoppingCart
        )

    @action(
        detail=False, methods=["get"], permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):

        # if not user.shopping_cart.exists():
        #     return Response(
        #         {"errors": "Shopping cart is empty"},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )

        return generate_shopping_list(self, request)


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


class SubscriptionListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """ViewSet for Subscription [GET-list]."""

    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageLimitPagination

    def get_queryset(self):
        return User.objects.filter(subscriptions__user=self.request.user)


class SubscriptionView(APIView):
    """ViewClass for Subscription [POST, DELETE]."""

    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        data = {"user": request.user.id, "author": user_id}
        serializer = SubscriptionCreateSerializer(
            data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        user = request.user
        author = get_object_or_404(User, id=user_id)
        instance = get_object_or_404(Subscription, user=user, author=author)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
