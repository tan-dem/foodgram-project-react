from django.contrib.auth.hashers import check_password
from djoser.serializers import (
    PasswordSerializer,
    UserCreateSerializer,
    UserSerializer,
)
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Subscription,
    Tag,
)
from users.models import User
from .validators import (
    validate_cooking_time,
    validate_ingredients,
    validate_tags,
)


def custom_to_representation(self, instance, serializer):
    request = self.context.get("request")
    context = {"request": request}
    data = serializer(instance, context=context).data
    return data


class CustomUserCreateSerializer(UserCreateSerializer):
    """User model serializer, write only."""

    class Meta:
        model = User
        fields = ("email", "username", "first_name", "last_name", "password")
        required_fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
        )


class UserProfileSerializer(UserSerializer):
    """User model serializer, read only."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        return (
            self.context.get("request").user.is_authenticated
            and Subscription.objects.filter(
                user=self.context.get("request").user, author=obj
            ).exists()
        )


class SetPasswordSerializer(PasswordSerializer):
    """Serializer for setting password of the current user."""

    current_password = serializers.CharField(
        required=True, label="Current password"
    )

    def validate(self, data):
        user = self.context.get("request").user
        if data["new_password"] == data["current_password"]:
            raise serializers.ValidationError(
                {"new_password": "New password must be different"}
            )
        check_current = check_password(data["current_password"], user.password)
        if check_current is False:
            raise serializers.ValidationError(
                {"current_password": "Invalid password"}
            )
        return data


class SubscriptionSerializer(UserProfileSerializer):
    """Subscription model serializer, read only."""

    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta(UserProfileSerializer.Meta):
        fields = UserProfileSerializer.Meta.fields + (
            "recipes", "recipes_count"
        )

    def get_recipes(self, obj):
        request = self.context.get("request")
        recipes = obj.recipes.all()
        recipes_limit = request.query_params.get("recipes_limit")
        if recipes_limit:
            recipes = recipes[: int(recipes_limit)]
        return RecipeShortSerializer(recipes, many=True).data

    @staticmethod
    def get_recipes_count(obj):
        return obj.recipes.count()


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    """Subscription model serializer, write only."""

    class Meta:
        model = Subscription
        fields = ("user", "author")
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=("user", "author"),
                message="You are already subscribed to this user",
            )
        ]

    def validate(self, data):
        if data["user"] == data["author"]:
            raise serializers.ValidationError(
                "You cannot subscribe to yourself"
            )
        return data

    def to_representation(self, instance):
        return custom_to_representation(
            self, instance.author, SubscriptionSerializer
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Ingredient model serializer."""

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class TagSerializer(serializers.ModelSerializer):
    """Tag model serializer."""

    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """RecipeIngredient model serializer."""

    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeShortSerializer(serializers.ModelSerializer):
    """Serializer for short representation of Recipe (add to ShoppingCart)."""

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class RecipeIngredientShortSerializer(serializers.ModelSerializer):
    """Serializer for short representation of Ingredient (add to Recipe)."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ("id", "amount")


class RecipeReadSerializer(serializers.ModelSerializer):
    """Recipe model serializer, read only."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserProfileSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = "__all__"

    def get_ingredients(self, obj):
        queryset = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(queryset, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj
        ).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Recipe model serializer, write only."""

    ingredients = RecipeIngredientShortSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField()
    author = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
        )

    def validate(self, data):
        return (
            validate_cooking_time(self, data) and
            validate_ingredients(self, data) and
            validate_tags(self, data)
        )

    @staticmethod
    def create_ingredients(ingredients, recipe):
        for ingredient in ingredients:
            RecipeIngredient.objects.bulk_create([
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient["id"],
                    amount=ingredient["amount"],
                )
            ])

    @staticmethod
    def create_tags(tags, recipe):
        for tag in tags:
            recipe.tags.add(tag)

    def create(self, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data)
        self.create_tags(tags, recipe)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def to_representation(self, instance):
        return custom_to_representation(
            self, instance, RecipeReadSerializer
        )

    def update(self, instance, validated_data):
        instance.tags.clear()
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.create_tags(validated_data.pop("tags"), instance)
        self.create_ingredients(validated_data.pop("ingredients"), instance)
        return super().update(instance, validated_data)


class FavoriteSerializer(serializers.ModelSerializer):
    """Favorite model serializer."""

    class Meta:
        model = Favorite
        fields = ("user", "recipe")
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=("user", "recipe"),
                message="This recipe is already in favorites",
            )
        ]

    def to_representation(self, instance):
        return custom_to_representation(
            self, instance.recipe, RecipeShortSerializer
        )


class ShoppingCartSerializer(serializers.ModelSerializer):
    """ShoppingCart model serializer."""

    class Meta:
        model = ShoppingCart
        fields = ("user", "recipe")
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=("user", "recipe"),
                message="This recipe is already in shopping cart",
            )
        ]

    def to_representation(self, instance):
        return custom_to_representation(
            self, instance.recipe, RecipeShortSerializer
        )
