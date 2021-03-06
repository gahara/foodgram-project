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
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes')
    pub_date = models.DateTimeField(auto_now_add=True, db_index=True)
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    description = models.TextField()
    tags = models.ManyToManyField(Tag, related_name='recipes')
    ingredients = models.ManyToManyField(
        Ingredient, through='Content', through_fields=('recipe', 'ingredient')
    )
    cooking_time = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.title


class Content(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='contents')
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='contents')
    quantity = models.FloatField()

    def __str__(self):
        return self.ingredient.title


class Favourite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favourites',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favourites')

    def __str__(self):
        return self.recipe.title


class ShopList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shop_list'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='shop_list'
    )

    def __str__(self):
        return self.recipe.title
