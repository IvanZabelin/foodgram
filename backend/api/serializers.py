from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from api.services.fields import Base64ImageField
from api.services.serializer_helper import (
    add_ingredients,
    check_subscribe,
    check_recipe,
)
from recipes.models import (
    User,
    Subscribe,
    Tag,
    Ingredient,
    Recipe,
    RecipeIngredient,
    Favorite,
    ShoppingCart,
)
from api.services.constants import MIN_VALUE, MAX_VALUE, ERROR_MESSAGES


class UserSignUpSerializer(UserCreateSerializer):
    """Сериализатор создания пользователя."""

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
        )


class UserGetSerializer(UserSerializer):
    """Сериализатор получения информации о пользователе."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        return check_subscribe(self.context.get("request"), obj)


class UserSubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор подписки."""

    class Meta:
        model = Subscribe
        fields = "__all__"
        validators = [
            UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=("user", "author"),
                message=ERROR_MESSAGES["duplicate_subscription"],
            )
        ]

    def validate(self, data):
        request = self.context.get("request")
        if request.user == data["author"]:
            raise ValidationError(ERROR_MESSAGES["self_subscribe"])
        return data

    def to_representation(self, instance):
        request = self.context.get("request")
        return UserSubscribeRepresentSerializer(
            instance.author, context={"request": request}
        ).data


class UserSubscribeRepresentSerializer(UserGetSerializer):
    """Сериализатор получения информации о подписке."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )
        read_only_fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, obj):
        request = self.context.get("request")
        recipes_limit = None
        if request:
            recipes_limit = request.query_params.get("recipes_limit")
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = obj.recipes.all()[: int(recipes_limit)]
        return RecipeShortSerializer(
            recipes, many=True, context={"request": request}
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class TagGetSerializer(serializers.ModelSerializer):
    """Сериализатор получения информации о тегах."""

    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор работы с ингредиентами."""

    class Meta:
        model = Ingredient
        fields = "__all__"


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов в рецепте."""

    name = serializers.StringRelatedField(
        source="ingredient",
        read_only=True,
    )
    measurement_unit = serializers.StringRelatedField(
        source="ingredient.measurement_unit",
        read_only=True,
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )


class RecipeGetSerializer(serializers.ModelSerializer):
    """Сериализатор получения информации о рецептах."""

    tags = TagGetSerializer(
        many=True,
        read_only=True,
    )
    author = UserGetSerializer(
        read_only=True,
    )
    ingredients = RecipeIngredientSerializer(
        many=True,
        read_only=True,
        source="recipe_ingredients",
    )
    is_favorited = serializers.SerializerMethodField(
        read_only=True,
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        read_only=True,
    )

    class Meta:
        model = Recipe
        fields = "__all__"
        extra_fields = ("is_favorited", "is_in_shopping_cart")

    def get_is_favorited(self, obj):
        """Проверить наличие рецепта в избранном."""
        request = self.context.get("request")
        return check_recipe(request, obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        """Проверить наличие рецепта в списке покупок."""
        request = self.context.get("request")
        return check_recipe(request, obj, ShoppingCart)


class IngredientPostSerializer(serializers.ModelSerializer):
    """Сериализатор добавления ингредиентов в рецепт."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        min_value=MIN_VALUE,
        max_value=MAX_VALUE,
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "amount")


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецептов."""

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    ingredients = IngredientPostSerializer(
        many=True,
        source="recipe_ingredients",
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        min_value=MIN_VALUE,
        max_value=MAX_VALUE,
    )

    class Meta:
        model = Recipe
        fields = (
            "tags",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def validate(self, data):
        if not self.initial_data.get("ingredients"):
            raise ValidationError(ERROR_MESSAGES["missing_ingredients"])
        if not self.initial_data.get("tags"):
            raise ValidationError(ERROR_MESSAGES["missing_tags"])
        return data

    def validate_ingredients(self, ingredients):
        ingredients_list = []
        for item in ingredients:
            try:
                ingredient = Ingredient.objects.get(id=item["id"])
            except Ingredient.DoesNotExist:
                raise ValidationError(ERROR_MESSAGES["ingredient_not_found"])

            if ingredient in ingredients_list:
                raise ValidationError(ERROR_MESSAGES["duplicate_ingredient"])

            ingredients_list.append(ingredient)
        return ingredients

    def validate_tags(self, tags):
        if len(set(tags)) != len(tags):
            raise ValidationError(ERROR_MESSAGES["duplicate_tags"])
        return tags

    def create(self, validated_data):
        request = self.context.get("request")
        ingredients = validated_data.pop("recipe_ingredients")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        add_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop("recipe_ingredients")
        tags = validated_data.pop("tags")
        instance.tags.clear()
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        super().update(instance, validated_data)
        add_ingredients(ingredients, instance)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeGetSerializer(instance, context=self.context).data


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор краткой информации о рецепте."""

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор избранных рецептов."""

    class Meta:
        model = Favorite
        fields = "__all__"
        validators = [
            UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=["user", "recipe"],
                message=ERROR_MESSAGES["duplicate_favorite"],
            )
        ]

    def to_representation(self, instance):
        request = self.context.get("request")
        return RecipeShortSerializer(
            instance.recipe, context={"request": request}
        ).data


class ShoppingCartSerializer(FavoriteSerializer):
    """Сериализатор списка покупок."""

    class Meta:
        model = ShoppingCart
        fields = "__all__"
        validators = [
            UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=["user", "recipe"],
                message=ERROR_MESSAGES["duplicate_shopping"],
            )
        ]
