from django import forms
from django.forms import ModelForm

from .models import Recipe


class RecipeCreateForm(ModelForm):

    class Meta:
        model = Recipe
        fields = ('title', 'tags', 'time', 'description', 'image',)
        widgets = {'tags': forms.CheckboxSelectMultiple(), }


class RecipeForm(ModelForm):

    class Meta:
        model = Recipe
        fields = ('title', 'time', 'description', 'image',)
