from django import template
from products.models import Favourite, ShopList
from users.models import Subscription

register = template.Library()


@register.filter(name='is_favorite')
def is_favorite(request, recipe):
    if Favourite.objects.filter(
        user=request.user, recipe=recipe
    ).exists():
        return True

    return False


@register.filter(name='is_follower')
def is_follower(request, profile):
    if Subscription.objects.filter(
        user=request.user, author=profile
    ).exists():
        return True

    return False


@register.filter(name='is_in_purchases')
def is_in_purchases(request, recipe):

    if ShopList.objects.filter(
        user=request.user, recipe=recipe
    ).exists():
        return True

    return False


@register.filter(name='get_filter_values')
def get_filter_values(value):
    return value.getlist('filters')


@register.filter(name='get_filter_link')
def get_filter_values(request, tag):
    new_request = request.GET.copy()
    if tag.value in request.GET.getlist('filters'):
        filters = new_request.getlist('filters')
        filters.remove(tag.value)
        new_request.setlist('filters', filters)
    else:
        new_request.appendlist('filters', tag.value)
    return new_request.urlencode()
