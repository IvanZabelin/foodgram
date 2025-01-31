from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CustomDjoserUserViewSet,
    TagViewSet,
    IngredientViewSet,
    RecipeViewSet,
    UserSubscriptionsViewSet,
    UserSubscribeView,
)

router = DefaultRouter()
router.register(r"users", CustomDjoserUserViewSet, basename="users")
router.register(r"tags", TagViewSet, basename="tags")
router.register(r"ingredients", IngredientViewSet, basename="ingredients")
router.register(r"recipes", RecipeViewSet, basename="recipes")

urlpatterns = [
    path(
        "users/subscriptions/",
        UserSubscriptionsViewSet.as_view({"get": "list"}),
    ),
    path(
        "users/<int:user_id>/subscribe/",
        UserSubscribeView.as_view(),
    ),
    path("", include(router.urls)),
    path("auth/", include("djoser.urls.authtoken")),
]
