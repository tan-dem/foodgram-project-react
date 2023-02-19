from django.db import models
from django.core.validators import MinValueValidator

from users.models import User


class Ingredient(models.Model):
    """Ingredient model."""

    name = models.CharField(
        max_length=100,
        required=True,
        unique=True,
        verbose_name="Name",
    )
    measurement_unit = models.CharField(
        max_length=20,
        required=True,
        verbose_name="Measurement unit",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Recipe model."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes_by_author",
        verbose_name="Author",
    )
    name = models.CharField(
        max_length=200,
        required=True,
        verbose_name="Name",
    )
    image = models.ImageField(
        upload_to="images/",
        required=True,
        verbose_name="Image",
    )
    text = models.TextField(
        required=True,
        verbose_name="Description",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name="recipes",
        through="RecipeIngredient",
        verbose_name="Ingredients",
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="recipes",
        verbose_name="Tags",
    )
    cooking_time = models.PositiveIntegerField(
        required=True,
        validators=[MinValueValidator(1)],
        verbose_name="Cooking time",
        help_text="in minutes",
    )
    is_favorited = models.BooleanField(
        default=False,
        blank=False,
    )
    is_in_shopping_cart = models.BooleanField(
        default=False,
        blank=False,
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Model of connection recipes-ingredients."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Recipe",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ingredient",
    )
    amount = models.PositiveIntegerField(
        verbose_name="Quantity",
        validators=[MinValueValidator(1)],
    )

    class Meta:
        ordering = ["recipe"]

    def __str__(self):
        return f"{self.recipe} {self.ingredient}"

