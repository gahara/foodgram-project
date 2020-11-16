from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator

from foodgram.settings import PER_PAGE_COUNT
from .models import Tag

TAGS = ['lunch', 'dinner', 'breakfast']


def get_paginator(recipe_list, page_number):
    paginator = Paginator(recipe_list, PER_PAGE_COUNT)
    page = paginator.get_page(page_number)
    return page, paginator


def get_ingredients(request):
    ingredients = {}
    for key in request.POST:
        if key.startswith('nameIngredient'):
            ing_num = key[15:]
            ingredients[request.POST[key]] = request.POST[
                'valueIngredient_' + ing_num]
    return ingredients


def get_tags_for_edit(request):
    data = request.POST.copy()
    tags = []
    for value in TAGS:
        if value in data and data.get(value) == 'on':
            tag = get_object_or_404(Tag, value=value)
            tags.append(tag)

    return tags
