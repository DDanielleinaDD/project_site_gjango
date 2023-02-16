from django.core.paginator import Paginator


POST_RESTRICTION = 10


def paginator_func(request, posts):
    paginator = Paginator(posts, POST_RESTRICTION)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
