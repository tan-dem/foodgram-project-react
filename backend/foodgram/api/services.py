from django.conf import settings
from django.db.models import Sum
from django.http import HttpResponse
from rest_framework.decorators import action


@action(detail=False)
def generate_shopping_list(user):
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
    for item in shopping_cart:
        text += (
            f"{item[ingredient_name]} ({item[ingredient_unit]})"
            f" — {item[ingredient_qty_sum]}\n"
        )
    response = HttpResponse(text, content_type="text/plain")
    filename = settings.FILENAME_FOR_SERVICES
    response["Content-Disposition"] = f"attachment; filename={filename}"
    return response
