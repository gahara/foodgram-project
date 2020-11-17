from django.contrib import admin
from users.models import User

from .models import Favourite, Ingredient, Recipe, Tag


class UserAdmin(admin.ModelAdmin):
    list_filter = ('email', 'first_name',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('title', 'dimension',)
    list_filter = ('title',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'show_favorites')
    list_filter = ('author', 'title', 'tags',)

    def show_favorites(self, obj):
        result = Favourite.objects.filter(recipe=obj).count()
        return result

    show_favorites.short_description = 'Favourite'


class TagAdmin(admin.ModelAdmin):
    list_display = ('value', 'colour', 'name')


admin.site.register(User, UserAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
