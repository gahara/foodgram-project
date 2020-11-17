import csv
import json

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from users.models import Subscription, User

from .forms import RecipeCreateForm, RecipeForm
from .models import Content, Favourite, Ingredient, Recipe, ShopList, Tag
from .utils import get_ingredients, get_paginator, get_tags_for_edit

DEFAULT_TAGS = ['breakfast', 'lunch', 'dinner']
all_tags = Tag.objects.all()


def page_not_found(request, exception):
    return render(request, 'misc/404.html', {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'misc/500.html', status=500)


def list_ingredients(request):
    text = request.GET['query']

    ingredients_presentable = list(
        Ingredient.objects.filter(
            title__istartswith=text).values(
            'title',
            'dimension'))

    return JsonResponse(ingredients_presentable, safe=False)


def user_profile(request, username):
    tags = request.GET.getlist('filters')

    if not tags:
        tags = DEFAULT_TAGS

    profile = get_object_or_404(User, username=username)

    recipes = Recipe.objects.filter(author=profile).filter(
        tags__value__in=tags).select_related('author').distinct()

    can_follow = request.user.is_authenticated and request.user != profile

    page_number = request.GET.get('page')
    page, paginator = get_paginator(recipes, page_number)

    return render(request, 'authorRecipe.html', {
        'paginator': paginator,
        'page': page,
        'profile': profile,
        'follow_button': can_follow,
        'all_tags': all_tags,
        'tags_list': tags,
    })


def index(request):
    tags = request.GET.getlist('filters')

    if not tags:
        tags = DEFAULT_TAGS

    recipes = Recipe.objects.filter(tags__value__in=tags).select_related(
        'author').prefetch_related('tags').distinct()

    page_number = request.GET.get('page')
    page, paginator = get_paginator(recipes, page_number)

    shop_list_ids = list(ShopList.objects.values_list('recipe_id', flat=True))

    response = {
        'paginator': paginator,
        'page': page,
        'shop_list_ids': shop_list_ids,
        'all_tags': all_tags,
        'tags_list': tags,
    }

    if not request.user.is_authenticated:
        return render(request, 'indexNotAuth.html', response)

    favourites_ids = list(
        Favourite.objects.values_list(
            'recipe_id', flat=True))
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

    form = RecipeCreateForm(request.POST or None, files=request.FILES or None)

    if form.is_valid():
        new_recipe = form.save(commit=False)
        new_recipe.author = request.user
        new_recipe.save()

        ingredients = get_ingredients(request)

        for title, quantity in ingredients.items():
            ingredient = get_object_or_404(Ingredient, title=title)
            content = Content(
                recipe=new_recipe,
                ingredient=ingredient,
                quantity=quantity)
            content.save()

        form.save_m2m()

        return redirect(
            'recipe',
            recipe_id=new_recipe.id,
            username=request.user.username)
    return render(request, 'formRecipe.html', {'form': form})


@login_required
def delete_recipe(request, username, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    author = get_object_or_404(User, id=recipe.author_id)

    if request.user != author:
        return redirect('recipe', username=username, recipe_id=recipe_id)

    recipe.delete()
    return redirect('index')


@login_required
def edit_recipe(request, username, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    author = get_object_or_404(User, id=recipe.author_id)

    recipe_tags = recipe.tags.values_list('value', flat=True)

    if request.user != author:
        return redirect('recipe', username=username, recipe_id=recipe_id)

    form = RecipeForm(
        request.POST,
        files=request.FILES or None,
        instance=recipe)

    if form.is_valid():
        new_tags = get_tags_for_edit(request)
        new_recipe = form.save(commit=False)
        new_recipe.author = request.user
        new_recipe.save()
        new_recipe.contents.all().delete()
        ingredients = get_ingredients(request)
        for title, quantity in ingredients.items():
            ingredient = Ingredient.objects.get(title=title)
            content = Content(
                recipe=new_recipe,
                ingredient=ingredient,
                quantity=quantity)
            content.save()

        new_recipe.tags.set(new_tags)
        return redirect(
            'recipe',
            recipe_id=recipe.id,
            username=request.user.username)

    form = RecipeForm(instance=recipe)
    return render(request, 'formChangeRecipe.html', {
        'form': form,
        'recipe': recipe,
        'all_tags': all_tags,
        'recipe_tags': recipe_tags,
    })


@login_required
def favourites(request):
    tags = request.GET.getlist('filters')

    if not tags:
        tags = DEFAULT_TAGS

    recipes = Recipe.objects.filter(
        favourites__user=request.user).filter(
        tags__value__in=tags).distinct()

    page_number = request.GET.get('page')
    page, paginator = get_paginator(recipes, page_number)

    return render(request, 'favorites.html', {
        'paginator': paginator,
        'page': page,
        'all_tags': all_tags,
        'tags_list': tags,
    })


@login_required
@require_http_methods(['POST', 'DELETE'])
def change_favourites(request, recipe_id):
    if request.method == 'POST':
        recipe_id = json.loads(request.body).get('id')
        recipe = get_object_or_404(Recipe, pk=recipe_id)

        obj, created = Favourite.objects.get_or_create(
            user=request.user, recipe=recipe)

        return JsonResponse({'success': created})

    elif request.method == 'DELETE':
        recipe = get_object_or_404(Recipe, pk=recipe_id)

        removed = Favourite.objects.filter(
            user=request.user, recipe=recipe).delete()

        return JsonResponse({'success': bool(removed)})


@login_required
def shop_list(request):
    if request.GET:
        recipe_id = request.GET.get('recipe_id')
        ShopList.objects.get(recipe__id=recipe_id).delete()

    purchases = Recipe.objects.filter(shop_list__user=request.user)

    return render(request, 'shopList.html', {'purchases': purchases})


@login_required
def get_purchases(request):
    recipes = Recipe.objects.filter(shop_list__user=request.user)

    ingredients_needed = {}

    for recipe in recipes:
        ingredients = recipe.ingredients.values_list('title', 'dimension')
        content = recipe.contents.values_list('quantity', flat=True)

        for num in range(len(ingredients)):
            title, dimension = ingredients[num]
            quantity = content[num]
            ingredients_needed[title] = [
                ingredients_needed.get(
                    title, [0])[0] + quantity, dimension]

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

        obj, created = ShopList.objects.get_or_create(
            user=request.user, recipe=recipe)

        return JsonResponse({'sucess': created})

    elif request.method == 'DELETE':
        recipe = get_object_or_404(Recipe, pk=recipe_id)

        removed = ShopList.objects.filter(
            user=request.user, recipe=recipe).delete()
        return JsonResponse({'success': bool(removed)})


@login_required
@require_http_methods(['POST', 'DELETE'])
def subscriptions(request, author_id):

    if request.method == 'POST':
        author_id = json.loads(request.body).get('id')
        author = get_object_or_404(User, id=author_id)

        obj, created = Subscription.objects.get_or_create(
            reader=request.user, author=author)

        return JsonResponse({'success': created})

    elif request.method == 'DELETE':
        author = get_object_or_404(User, id=author_id)

        removed = Subscription.objects.filter(
            reader=request.user, author=author).delete()
        return JsonResponse({'success': bool(removed)})


@login_required
def my_follow_list(request):
    my_subscriptions = User.objects.filter(
        following__reader=request.user).annotate(
        recipe_count=Count('recipes'))

    recipe: dict = {}
    for sub in my_subscriptions:
        recipe[sub] = Recipe.objects.filter(author=sub)[:3]

    page_number = request.GET.get('page')
    page, paginator = get_paginator(my_subscriptions, page_number)

    return render(request, 'myFollow.html', {
        'paginator': paginator,
        'page': page,
        'recipe': recipe,
    })
