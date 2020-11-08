from django.db import models

from users.models import User


class Tag(models.Model):
    value = models.CharField(max_length=10, null=True)
    colour = models.CharField(max_length=10, null=True)
    name = models.CharField(max_length=10, null=True)

    def __str__(self):
        return self.value


class Ingredient(models.Model):
    title = models.CharField(max_length=200)
    dimension = models.CharField(max_length=50)

    def __str__(self):
        return self.title


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    pub_date = models.DateTimeField(auto_now_add=True, db_index=True)
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    description = models.TextField()
    tags = models.ManyToManyField(Tag, related_name='recipes')
    ingredients = models.ManyToManyField(
        Ingredient, through='Content', through_fields=('recipe', 'ingredient')  #https://djbook.ru/rel1.9/ref/models/fields.html
    )
    cooking_time = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.title


class Content(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_content')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='ingredients')
    quantity = models.FloatField()

    def __str__(self):
        return self.ingredient.title


class Favourite(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='favourite_recipes',)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favourites')

    def __str__(self):
        return self.recipe.title
