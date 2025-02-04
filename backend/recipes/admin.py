from django.contrib import admin
from django.utils.safestring import mark_safe
from django import forms
from django.db import models
from django.apps import apps
from django.contrib.auth.models import Group

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Subscribe,
    Tag,
    User,
)

# Убираем стандартные группы пользователей
admin.site.unregister(Group)

# Убираем отображение модели токенов (с обработкой исключения)
Token = apps.get_model("authtoken", "Token")
if Token:
    try:
        admin.site.unregister(Token)
        print("Модель токена успешно отменена.")
    except admin.sites.NotRegistered:
        print("Модель токена не зарегистрирована.")


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email")
    search_fields = ("username", "email")
    list_filter = ("username", "email")
    list_display_links = ("username",)


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "author")
    search_fields = ("user", "author")
    list_filter = ("user", "author")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    search_fields = ("name", "slug")
    list_display_links = ("name",)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "measurement_unit")
    search_fields = ("name",)
    list_filter = ("name",)
    list_display_links = ("name",)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "author", "favorites_amount", "get_img")
    search_fields = ("name", "author")
    list_filter = ("name", "author", "tags")
    list_display_links = ("name",)
    inlines = (RecipeIngredientInline,)
    readonly_fields = ["favorites_amount"]

    @admin.display(description="Добавлено в избранное")
    def favorites_amount(self, obj):
        return obj.favorites.count()

    @admin.display(description="Изображение")
    def get_img(self, obj):
        if obj.image:
            return mark_safe(f"<img src='{obj.image.url}' width=50 />")
        return "-"

    @admin.display(description="Теги")
    def get_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])

    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(
            attrs={'rows': 3, 'cols': 50}
        )},
    }

    autocomplete_fields = ['tags']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipe")
    search_fields = ("user", "recipe")


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipe")
    search_fields = ("user", "recipe")
