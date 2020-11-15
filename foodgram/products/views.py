import json
import csv

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, get_object_or_404, redirect

from .models import Content, Favourite, Ingredient, Recipe, ShopList, Tag
from .forms import RecipeCreateForm, RecipeForm
from users.models import User, Subscription
from .utils import get_paginator, get_ingredients, get_tags_for_edit

all_tags = Tag.objects.all()


def list_ingredients(request):
    text = request.GET['query']

    ingredients = Ingredient.objects.filter(title__istartswith=text)
    ingredients_list = []

    for ingredient in ingredients:
        ingredients_list.append({
            'title': ingredient.title,
            'dimension': ingredient.dimension
        })

    return JsonResponse(ingredients_list, safe=False)


def user_profile(request, username):
    tags_list = request.GET.getlist('filters')

    if not tags_list:
        tags_list = ['breakfast', 'lunch', 'dinner']

    profile = get_object_or_404(User, username=username)

    recipe_list = Recipe.objects.filter(author=profile)\
        .filter(tags__value__in=tags_list)\
        .select_related('author')\
        .distinct()

    can_follow = request.user.is_authenticated and request.user != profile

    page_number = request.GET.get('page')
    page, paginator = get_paginator(recipe_list, page_number)

    return render(request, 'authorRecipe.html', {
        'paginator': paginator,
        'page': page,
        'profile': profile,
        'follow_button': can_follow,
        'all_tags': all_tags,
        'tags_list': tags_list,
        })


def index(request):
    tags_list = request.GET.getlist('filters')

    if not tags_list:
        tags_list = ['breakfast', 'lunch', 'dinner']

    recipe_list = Recipe.objects.filter(tags__value__in=tags_list)\
        .select_related('author')\
        .prefetch_related('tags')\
        .distinct()

    page_number = request.GET.get('page')
    page, paginator = get_paginator(recipe_list, page_number)

    shop_list_ids = [shl_id for shl_id in ShopList.objects.values_list('recipe_id', flat=True)]

    response = {
            'paginator': paginator,
            'page': page,
            'shop_list_ids': shop_list_ids,
            'all_tags': all_tags,
            'tags_list': tags_list,
        }

    if not request.user.is_authenticated:
        return render(request, 'indexNotAuth.html', response)

    favourites_ids = [f_id for f_id in Favourite.objects.values_list('recipe_id', flat=True)]
    shop_list_count = ShopList.objects.filter(user=request.user).count()

    response['favourites_ids'] = favourites_ids
    response['shop_list_count'] = shop_list_count

    return render(request, 'indexAuth.html', response)


def view_recipe(request, username, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)

    if not request.user.is_authenticated:
        return render(
            request,
            'singlePageNotAuth.html',
            {'recipe': recipe}
        )

    user_profile = get_object_or_404(User, username=username)
    is_owner = request.user == recipe.author

    return render(request, 'singlePage.html', {
        'recipe': recipe,
        'owner': is_owner,
        'profile': user_profile,
    })


def create_recipe(request):
    if request.method == 'POST':
        form = RecipeCreateForm(request.POST or None, files=request.FILES or None)

        if form.is_valid():
            new_recipe = form.save(commit=False)
            new_recipe.author = request.user
            new_recipe.save()

            ingredients = get_ingredients(request)

            for title, quantity in ingredients.items():
                ingredient = Ingredient.objects.get(title=title)
                content = Content(
                    recipe=new_recipe,
                    ingredient=ingredient,
                    quantity=quantity)
                content.save()

            form.save_m2m()

            return redirect('recipe', recipe_id=new_recipe.id, username=request.user.username)

    form = RecipeCreateForm()
    return render(request, 'formRecipe.html', {'form': form})


@login_required
def delete_recipe(request, username, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    author = get_object_or_404(User, id=recipe.author_id)

    if request.user != author:
        return redirect('recipe', username=username, recipe_id=recipe_id)

    recipe.delete()
    return redirect('/')


@login_required
def edit_recipe(request, username, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    author = get_object_or_404(User, id=recipe.author_id)

    recipe_tags = recipe.tags.values_list('value', flat=True)

    if request.user != author:
        return redirect('recipe', username=username, recipe_id=recipe_id)

    if request.method == 'POST':
        new_tags = get_tags_for_edit(request)
        form = RecipeForm(request.POST, files=request.FILES or None, instance=recipe)

        if form.is_valid():
            new_recipe = form.save(commit=False)
            new_recipe.author = request.user
            new_recipe.save()
            new_recipe.recipe_content.all().delete()
            ingredients = get_ingredients(request)
            for title, quantity in ingredients.items():
                ingredient = Ingredient.objects.get(title=title)
                content = Content(recipe=new_recipe, ingredient=ingredient, quantity=quantity)
                content.save()

            new_recipe.tags.set(new_tags)
            return redirect('recipe', recipe_id=recipe.id, username=request.user.username)

    form = RecipeForm(instance=recipe)
    return render(request, 'formChangeRecipe.html', {
        'form': form,
        'recipe': recipe,
        'all_tags': all_tags,
        'recipe_tags': recipe_tags,
    })


@login_required
def favourites(request):
    tags_list = request.GET.getlist('filters')

    if not tags_list:
        tags_list = ['breakfast', 'lunch', 'dinner']

    recipe_list = Recipe.objects.filter(favourite_recipes__user=request.user).filter(tags__value__in=tags_list).distinct()

    page_number = request.GET.get('page')
    page, paginator = get_paginator(recipe_list, page_number)

    return render(request, 'favorites.html', {
        'paginator': paginator,
        'page': page,
        'all_tags': all_tags,
        'tags_list': tags_list,
    })


@login_required
@require_http_methods(['POST', 'DELETE'])
def change_favourites(request, recipe_id):
    if request.method == 'POST':
        recipe_id = json.loads(request.body).get('id')
        recipe = get_object_or_404(Recipe, pk=recipe_id)

        obj, created = Favourite.objects.get_or_create(user=request.user, recipe=recipe)

        return JsonResponse({'success': created})

    elif request.method == 'DELETE':
        recipe = get_object_or_404(Recipe, pk=recipe_id)

        removed = Favourite.objects.filter(user=request.user, recipe=recipe).delete()

        return JsonResponse({'success': bool(removed)})
   
    
@login_required
def shop_list(request):
    if request.GET:
        recipe_id = request.GET.get('recipe_id')
        ShopList.objects.get(recipe__id=recipe_id).delete()

    purchases_list = Recipe.objects.filter(shop_list__user=request.user)

    return render(request, 'shopList.html', {'purchases': purchases_list})


@login_required
def get_purchases(request):
    recipes = Recipe.objects.filter(shop_list__user=request.user)

    ingredients_needed: dict = {}

    for recipe in recipes:
        ingredients = recipe.ingredients.values_list('title', 'dimension')
        content = recipe.recipe_content.values_list('quantity', flat=True)

        for num in range(len(ingredients)):
            title: str = ingredients[num][0]
            dimension: str = ingredients[num][1]
            quantity: int = content[num]

            if title in ingredients_needed.keys():
                ingredients_needed[title] = [ingredients_needed[title][0] + quantity, dimension]
            else:
                ingredients_needed[title] = [quantity, dimension]

    response = HttpResponse(content_type='txt/csv')
    writer = csv.writer(response)

    for key, value in ingredients_needed.items():
        writer.writerow([f'{key} ({value[1]}) - {value[0]}'])

    return response


@login_required
@require_http_methods(['POST', 'DELETE'])
def purchases(request, recipe_id):

    if request.method == 'POST':
        recipe_id = json.loads(request.body).get('id')
        recipe = get_object_or_404(Recipe, pk=recipe_id)

        obj, created = ShopList.objects.get_or_create(user=request.user, recipe=recipe)

        return JsonResponse({'sucess': created})

    elif request.method == 'DELETE':
        recipe = get_object_or_404(Recipe, pk=recipe_id)

        removed = ShopList.objects.filter(user=request.user, recipe=recipe).delete()
        return JsonResponse({'success': bool(removed)})


@login_required
@require_http_methods(['POST', 'DELETE'])
def subscriptions(request, author_id):

    if request.method == 'POST':
        author_id = json.loads(request.body).get('id')
        author = get_object_or_404(User, id=author_id)

        obj, created = Subscription.objects.get_or_create(reader=request.user, author=author)

        return JsonResponse({'success': created})

    elif request.method == 'DELETE':
        author = get_object_or_404(User, id=author_id)

        removed = Subscription.objects.filter(reader=request.user, author=author).delete()
        return JsonResponse({'success': bool(removed)})


@login_required
def my_follow_list(request):
    subscriptions_list = User.objects.filter(following__reader=request.user).annotate(recipe_count=Count('recipes'))

    recipe: dict = {}
    for sub in subscriptions:
        recipe[sub] = Recipe.objects.filter(author=sub)[:3]

    page_number = request.GET.get('page')
    page, paginator = get_paginator(subscriptions_list, page_number)

    return render(request, 'myFollow.html', {
        'paginator': paginator,
        'page': page,
        'recipe': recipe,
    })
