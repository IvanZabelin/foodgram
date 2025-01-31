from django_filters.rest_framework import DjangoFilterBackend
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import ValidationError

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAdminAuthorOrReadOnly
from api.serializers import (
    AvatarSerializer,
    TagGetSerializer,
    IngredientSerializer,
    RecipeGetSerializer,
    RecipeCreateUpdateSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer,
    UserSubscribeSerializer,
    UserSubscribeRepresentSerializer,
)
from api.services.view_helper import RecipeProcessor, get_shopping_cart

from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    Favorite,
    ShoppingCart,
    User,
)


class CustomDjoserUserViewSet(DjoserUserViewSet):
    """Пользователь."""

    @action(
        detail=False, methods=["GET"], permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'delete'], permission_classes=[
        IsAuthenticated], url_path='me/avatar')
    def avatar(self, request):
        """Управление аватаром пользователя."""
        user = request.user

        if request.method == 'DELETE':
            if user.avatar:
                user.avatar.delete()
                user.avatar = None
                user.save()
                return Response(
                    {'avatar': None},
                    status=status.HTTP_204_NO_CONTENT)
            raise ValidationError({'error': 'Аватар отсутствует'})

        if "avatar" not in request.data:
            return Response(
                {"error": "Поле 'avatar' обязательно."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AvatarSerializer(user, data=request.data, partial=True)

        if not serializer.is_valid():
            raise ValidationError(serializer.errors)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserSubscribeView(APIView):
    """Подписка на пользователя."""

    permission_classes = (IsAdminAuthorOrReadOnly,)

    def post(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        serializer = UserSubscribeSerializer(
            data={"user": request.user.id, "author": author.id},
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        follower = request.user.follower.filter(author=author)
        if not follower:
            return Response(
                {"error": "Нет подписки на этого пользователя"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        follower.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserSubscriptionsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Получение списка всех подписок на пользователей."""

    serializer_class = UserSubscribeRepresentSerializer

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)


class TagViewSet(ModelViewSet):
    """Тег."""

    http_method_names = ["get"]
    queryset = Tag.objects.all()
    serializer_class = TagGetSerializer
    pagination_class = None


class IngredientViewSet(ModelViewSet):
    """Ингредиент."""

    http_method_names = ["get"]
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    """Рецепт."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAdminAuthorOrReadOnly,)
    http_method_names = ["get", "post", "patch", "delete"]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return RecipeGetSerializer
        return RecipeCreateUpdateSerializer

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk):
        recipe_processor = RecipeProcessor()
        err_msg = "Рецепт отсутствует в избранном."
        return recipe_processor.execute(
            FavoriteSerializer, Favorite, request, pk, err_msg
        )

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk):
        """Добавление или удаление рецепта в список покупок."""
        recipe_processor = RecipeProcessor()
        err_msg = "Рецепт отсутствует в списке покупок."
        return recipe_processor.execute(
            ShoppingCartSerializer, ShoppingCart, request, pk, err_msg
        )

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        return get_shopping_cart(request)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        """Генерация короткой ссылки на рецепт."""
        recipe = get_object_or_404(Recipe, pk=pk)
        short_url = request.build_absolute_uri(
            reverse('short_link', args=[recipe.pk])
        )
        return Response({'short-link': short_url}, status=status.HTTP_200_OK)


def short_link_view(request, id):
    """Перенаправление на рецепт по короткой ссылке."""
    try:
        recipe = Recipe.objects.get(pk=id)
        return redirect('recipe_detail', pk=recipe.pk)
    except Recipe.DoesNotExist:
        return redirect('404_page')
