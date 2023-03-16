from django.core.validators import MinValueValidator
from django.db import models
from users.models import User


class Ingredient(models.Model):
    """Ingredient model."""

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Name",
    )
    measurement_unit = models.CharField(
        max_length=20,
        verbose_name="Measurement unit",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Tag model."""

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Name",
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        verbose_name="Color",
    )
    slug = models.SlugField(
        unique=True,
        verbose_name="Slug",
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
        related_name="recipes",
        verbose_name="Author",
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Name",
    )
    image = models.ImageField(
        upload_to="images/",
        verbose_name="Image",
    )
    text = models.TextField(
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
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Cooking time",
        help_text="in minutes",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Supportive model for recipes & ingredients relation."""

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
    amount = models.PositiveSmallIntegerField(
        verbose_name="Quantity",
        validators=[MinValueValidator(1)],
    )

    class Meta:
        ordering = ["recipe"]

    def __str__(self):
        return f"{self.ingredient} in {self.recipe}"


class Subscription(models.Model):
    """Subscription model."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscriber",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"],
                name="unique_subscription",
            )
        ]

    def __str__(self):
        return f"{self.user} is subscribed to {self.author}"


class Favorite(models.Model):
    """Favorite model."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorites",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="is_favorited",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_favorite",
            )
        ]

    def __str__(self):
        return f"{self.recipe} is favorited by {self.user}"


class ShoppingCart(models.Model):
    """Shopping cart model."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="is_in_shopping_cart",
    )

    def __str__(self):
        return f"{self.recipe} is in shopping cart of {self.user}"
