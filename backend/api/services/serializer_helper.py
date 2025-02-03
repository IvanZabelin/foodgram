from recipes.models import Ingredient, RecipeIngredient


def check_recipe(request, obj, model):
    """Проверка рецепта."""
    return (
        request
        and request.user.is_authenticated
        and model.objects.filter(user=request.user, recipe=obj).exists()
    )


def check_subscribe(request, author):
    """Проверка подписки."""
    return (
        request.user.is_authenticated
        and request.user.follower.filter(author=author).exists()
    )


def add_ingredients(ingredients, recipe):
    """Добавить ингредиенты."""
    ingredient_list = [
        RecipeIngredient(
            recipe=recipe,
            ingredient=Ingredient.objects.get(id=ingredient.get("id")),
            amount=ingredient.get("amount"),
        )
        for ingredient in ingredients
    ]
    RecipeIngredient.objects.bulk_create(ingredient_list)
