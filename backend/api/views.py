from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAdminAuthorOrReadOnly
from api.serializers import (
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
