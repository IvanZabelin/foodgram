from recipes.models import RecipeIngredient


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


def add_ingredients(ingredients_data, recipe):
    """Добавление ингредиентов к рецепту с сохранением ID."""
    recipe_ingredients = []
    existing_ingredients = {
        ri.ingredient.id: ri
        for ri in RecipeIngredient.objects.filter(recipe=recipe)
    }

    for item in ingredients_data:
        ingredient_id = item["id"]
        amount = item["amount"]

        if ingredient_id in existing_ingredients:
            existing_ingredients[ingredient_id].amount = amount
            existing_ingredients[ingredient_id].save()
        else:
            recipe_ingredients.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient_id=ingredient_id,
                    amount=amount,
                )
            )

    if recipe_ingredients:
        RecipeIngredient.objects.bulk_create(recipe_ingredients)
