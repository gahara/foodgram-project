# Generated by Django 3.1.1 on 2020-11-16 19:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_shoplist'),
    ]

    operations = [
        migrations.AlterField(
            model_name='favourite',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favourites', to='products.recipe'),
        ),
    ]
