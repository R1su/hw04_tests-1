from django.core.paginator import Paginator
from django.conf import settings


def get_page(queryset, request):
    paginator = Paginator(queryset, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)