# Generated by Django 3.1.1 on 2020-11-16 19:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_auto_20201116_1921'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contents', to='products.recipe'),
        ),
    ]
