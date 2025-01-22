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


# Базовый сериализатор с общими методами
class BaseSerializer(serializers.ModelSerializer):
    """Базовый сериализатор с общими методами."""

    def to_representation(self, instance):
        """Переопределённое представление данных."""
        if hasattr(self.Meta, "representation_serializer"):
            return self.Meta.representation_serializer(instance, context=self.context).data
        return super().to_representation(instance)


class UserSignUpSerializer(UserCreateSerializer):
    """Сериализатор регистрации пользователя."""

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
    """Сериализатор информации о пользователе."""

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
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return request.user.follower.filter(author=obj).exists()


class UserSubscribeSerializer(BaseSerializer):
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
        if self.context["request"].user == data["author"]:
            raise ValidationError(ERROR_MESSAGES["self_subscribe"])
        return data

    class Meta:
        model = Subscribe
        fields = "__all__"
        representation_serializer = UserGetSerializer


class RecipeGetSerializer(BaseSerializer):
    """Сериализатор получения информации о рецептах."""

    tags = serializers.StringRelatedField(many=True, read_only=True)
    author = UserGetSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = "__all__"

    def get_ingredients(self, obj):
        return RecipeIngredient.objects.filter(recipe=obj).values(
            "id", "ingredient__name", "ingredient__measurement_unit", "amount"
        )

    def get_is_favorited(self, obj):
        return check_recipe(self.context.get("request"), obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return check_recipe(self.context.get("request"), obj, ShoppingCart)


class RecipeCreateUpdateSerializer(BaseSerializer):
    """Сериализатор создания и обновления рецептов."""

    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "tags",
            "ingredients",
            "image",
            "cooking_time",
        )
        representation_serializer = RecipeGetSerializer

    def validate_ingredients(self, ingredients):
        unique_ids = set()
        for ingredient in ingredients:
            if ingredient["id"] in unique_ids:
                raise ValidationError(ERROR_MESSAGES["duplicate_ingredient"])
            unique_ids.add(ingredient["id"])
        return ingredients

    def create(self, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        add_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.set(validated_data.pop("tags"))
        RecipeIngredient.objects.filter(recipe=instance).delete()
        add_ingredients(validated_data.pop("ingredients"), instance)
        return super().update(instance, validated_data)
