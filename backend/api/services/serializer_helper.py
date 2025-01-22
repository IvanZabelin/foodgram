from rest_framework import serializers

from recipes.models import Ingredient, RecipeIngredient


def check_recipe(request, obj, model):
    """Проверка, находится ли рецепт в указанной модели у текущего пользователя."""
    if not request or not request.user.is_authenticated:
        return False
    return model.objects.filter(user=request.user, recipe=obj).exists()


def check_subscribe(request, author):
    """Проверка, подписан ли пользователь на автора."""
    if not request or not request.user.is_authenticated:
        return False
    return request.user.follower.filter(author=author).exists()


def add_ingredients(ingredients, recipe):
    """Добавление ингредиентов к рецепту."""
    ingredient_list = []
    for ingredient_data in ingredients:
        try:
            ingredient = Ingredient.objects.get(id=ingredient_data.get("id"))
            ingredient_list.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=ingredient_data.get("amount"),
                )
            )
        except Ingredient.DoesNotExist:
            raise serializers.ValidationError(
                f"Ингредиент с id={ingredient_data.get('id')} не найден."
            )
    RecipeIngredient.objects.bulk_create(ingredient_list)
