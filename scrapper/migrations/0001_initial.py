# Generated by Django 4.2 on 2023-04-26 18:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="Review",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("author", models.TextField(max_length=20)),
                ("rating", models.TextField(max_length=3)),
                ("recommendation", models.TextField(max_length=15)),
                ("confirmed", models.TextField(max_length=50)),
                ("purchase_date", models.TextField(max_length=20)),
                ("review_date", models.TextField(max_length=20)),
                ("description", models.TextField(max_length=500)),
                ("vote_up", models.IntegerField()),
                ("vote_down", models.IntegerField()),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to="scrapper.product",
                    ),
                ),
            ],
        ),
    ]
