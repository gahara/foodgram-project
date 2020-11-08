from django.contrib import admin

from .models import (Ingredient, Recipe,
                     Tag)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('title', 'dimension',)
    list_filter = ('title',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'author')
    list_filter = ('author', 'title', 'tags',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('value', 'colour', 'name')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
