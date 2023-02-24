from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Subscription, Tag)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "name",
        "measurement_unit",
    )
    list_filter = ("name",)
    search_fields = ("name",)
    empty_value_display = "-empty-"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "name",
        "slug",
    )
    empty_value_display = "-empty-"


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "name",
        "author",
        "is_favorited",
    )
    list_filter = (
        "author",
        "name",
        "tags",
    )
    empty_value_display = "-empty-"

    def is_favorited(self, obj):
        return f"Favorited {Favorite.objects.filter(recipe=obj).count()} times"


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "recipe",
        "ingredient",
    )
    list_editable = (
        "recipe",
        "ingredient",
    )
    empty_value_display = "-empty-"


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "user",
        "author",
    )
    list_editable = (
        "user",
        "author",
    )
    empty_value_display = "-empty-"


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "user",
        "recipe",
    )
    list_editable = (
        "user",
        "recipe",
    )
    empty_value_display = "-empty-"


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "user",
        "recipe",
    )
    list_editable = (
        "user",
        "recipe",
    )
    empty_value_display = "-empty-"
