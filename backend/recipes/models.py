from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models

from .validators import username_validator, color_validator


class LENGTH:
    l_150 = 150
    l_200 = 200
    l_254 = 254
    l_7 = 7


class User(AbstractUser):
    """Модель пользователя."""
    username = models.CharField(
        verbose_name="username",
        max_length=LENGTH.l_150,
        unique=True,
        validators=[username_validator],
    )
    email = models.EmailField(
        verbose_name="email",
        max_length=LENGTH.l_254,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name="Имя",
        max_length=LENGTH.l_150,
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=LENGTH.l_150,
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["username"]

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    """Модель подписки."""
    user = models.ForeignKey(
        User,
        verbose_name="Подписчик",
        on_delete=models.CASCADE,
        related_name="follower",
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name="following",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        ordering = ["author"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"],
                name="unique_user_author",
            )
        ]

    def __str__(self):
        return f"{self.user.username} подписан на {self.author.username}"


class Tag(models.Model):
    """Модель тегов."""
    name = models.CharField(
        verbose_name="Название",
        max_length=LENGTH.l_200,
        unique=True,
    )
    color = models.CharField(
        verbose_name="Цвет",
        max_length=LENGTH.l_7,
        unique=True,
        validators=[color_validator],
    )
    slug = models.SlugField(
        verbose_name="Слаг",
        max_length=LENGTH.l_200,
        unique=True,
        db_index=True,
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов."""
    name = models.CharField(
        verbose_name="Название",
        max_length=LENGTH.l_200,
        db_index=True,
    )
    measurement_unit = models.CharField(
        verbose_name="Единица измерения",
        max_length=LENGTH.l_200,
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""
    name = models.CharField(
        verbose_name="Название",
        max_length=LENGTH.l_200,
    )
    text = models.TextField(
        verbose_name="Описание",
    )
    image = models.ImageField(
        verbose_name="Изображение",
        upload_to="recipes/",
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name="recipes",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through="RecipeIngredient",
        related_name="recipes",
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления",
        validators=[MinValueValidator(1)],
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Теги",
        related_name="recipes",
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ["-id"]

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Модель рецепт-ингридиент."""
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт",
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name="Ингредиент",
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
    )
    amount = models.PositiveBigIntegerField(
        verbose_name="Количество",
        validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецептах"
        db_table = "recipes_recipe_ingredient"
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="unique_recipe_ingredient"
            )
        ]

    def __str__(self):
        return (
            f"{self.recipe.name}: "
            f"{self.ingredient.name} - "
            f"{self.amount}/"
            f"{self.ingredient.measurement_unit}"
        )


class Favorite(models.Model):
    """Модель избранного."""

    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        related_name="favorites",
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт",
        on_delete=models.CASCADE,
        related_name="favorites",
    )
    created = models.DateTimeField(
        verbose_name="Дата добавления",
        auto_now_add=True,
    )
    
    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_user_favorite",
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.recipe}"


class ShoppingCart(models.Model):
    """Модель списка покупок."""

    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        related_name="carts",
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт",
        on_delete=models.CASCADE,
        related_name="carts",
    )

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"
        db_table = "recipes_shopping_cart"
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_user_cart",
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.recipe}"
