from rest_framework.pagination import PageNumberPagination


class PageSizeLimitPagination(PageNumberPagination):
    """Пагинатор с лимитом."""
    page_size_query_param = 'limit'
