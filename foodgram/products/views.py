from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render

from .models import Content, Favourite, Ingredient, Recipe, ShopList, Tag
from users.models import User


def get_ingredients(request):
    text = request.GET['query']

    ingredients = Ingredient.objects.filter(
        title__istartswith=text
    )
    ingredients_list = []

    for ingredient in ingredients:
        ingredients_list.append({
            'title': ingredient.title,
            'dimension': ingredient.dimension
        })

    return JsonResponse(ingredients_list, safe=False)


def index(request):
    tags_list = request.GET.getlist('filters')

    recipe_list = Recipe.objects.filter(
        tags__value__in=tags_list
    ).select_related(
        'author'
    ).prefetch_related(
        'tags'
    ).distinct()

    all_tags = Tag.objects.all()

    shop_list_ids = [id for id in ShopList.objects.values_list(
        'recipe_id', flat=True
    )]

    favorites_ids = [id for id in Favourite.objects.values_list(
        'recipe_id', flat=True
    )]

    paginator = Paginator(recipe_list, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    if request.user.is_authenticated:
        shop_list_count = ShopList.objects.filter(user=request.user).count()

        return render(request, 'indexAuth.html', {
            'paginator': paginator,
            'page': page,
            'shop_list_ids': shop_list_ids,
            'favorites_ids': favorites_ids,
            'shop_list_count': shop_list_count,
            'all_tags': all_tags,
            'tags_list': tags_list,
        }
        )

    return render(request, 'indexNotAuth.html', {
        'paginator': paginator,
        'page': page,
        'shop_list_ids': shop_list_ids,
        'all_tags': all_tags,
        'tags_list': tags_list,
    }
    )
