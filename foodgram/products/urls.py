from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('new_recipe/', views.create_recipe, name='create_recipe'),
    path('favorites/', views.favourites, name='favourites'),
    path('ingredients/', views.list_ingredients, name='ingredients'),
    path('change_favorites/<int:recipe_id>/', views.change_favourites, name='change_favourites'),
    path('follow/', views.my_follow_list, name='my_follow'),
    path('shop_list/', views.shop_list, name='shop_list'),
    path('purchases/', views.get_purchases, name='get_purchases'),
    path('purchases/<int:recipe_id>/', views.purchases, name='purchases'),
    path('subscriptions/<int:author_id>/', views.subscriptions, name='subscriptions'),
    path('<str:username>/', views.user_profile, name='profile'),
    path('<str:username>/<int:recipe_id>/', views.view_recipe, name='recipe'),
    path('<str:username>/<int:recipe_id>/edit/', views.edit_recipe, name='edit_recipe'),
    path('<str:username>/<int:recipe_id>/delete/', views.delete_recipe, name='delete_recipe')
]
