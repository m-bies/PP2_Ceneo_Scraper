# Generated by Django 4.2 on 2023-05-06 12:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scrapper', '0003_disadvantages_advantages'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='advantages',
            field=models.ManyToManyField(blank=True, to='scrapper.advantages'),
        ),
        migrations.AddField(
            model_name='review',
            name='disadvantages',
            field=models.ManyToManyField(blank=True, to='scrapper.disadvantages'),
        ),
        migrations.AlterField(
            model_name='advantages',
            name='reviews',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='advantages_list', to='scrapper.review'),
        ),
        migrations.AlterField(
            model_name='disadvantages',
            name='reviews',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='disadvantages_list', to='scrapper.review'),
        ),
    ]
