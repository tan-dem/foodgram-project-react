from rest_framework import serializers


def validate_ingredients(self, data):
    ingredients = data["ingredients"]
    ingredients_list = []
    for ingredient in ingredients:
        ingredient_id = ingredient["id"]
        if ingredient_id in ingredients_list:
            raise serializers.ValidationError(
                {"ingredients": "This ingredient was already added"}
            )
        ingredients_list.append(ingredient_id)
        amount = ingredient["amount"]
        if int(amount) <= 0:
            raise serializers.ValidationError(
                {"amount": "Quantity of ingredient must be > 0"}
            )
    return data


def validate_tags(self, data):
    tags = data["tags"]
    if not tags:
        raise serializers.ValidationError(
            {"tags": "Choose at least 1 tag"}
        )
    tags_list = []
    for tag in tags:
        if tag in tags_list:
            raise serializers.ValidationError(
                {"tags": "This tag was already added"}
            )
        tags_list.append(tag)
    return data


def validate_cooking_time(self, data):
    cooking_time = data["cooking_time"]
    if int(cooking_time) <= 0:
        raise serializers.ValidationError(
            {"cooking_time": "Cooking time must be > 0"}
        )
    return data
