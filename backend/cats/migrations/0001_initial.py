# Generated migration to work with existing PostgreSQL table

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        # Since the table already exists in PostgreSQL, we use a RunSQL operation
        # that does nothing but tells Django the table exists
        migrations.RunSQL(
            "SELECT 1;",  # No-op SQL command
            reverse_sql="SELECT 1;",  # No-op SQL command for rollback
        ),
        # Create the model state without actually creating the table
        migrations.CreateModel(
            name="Cat",
            fields=[
                ("id", models.AutoField(primary_key=True)),
                ("name", models.CharField(help_text="The cat's name", max_length=100)),
                (
                    "breed",
                    models.CharField(
                        blank=True,
                        help_text="The cat's breed (optional)",
                        max_length=100,
                        null=True,
                    ),
                ),
                (
                    "age",
                    models.IntegerField(
                        blank=True, help_text="The cat's age in years", null=True
                    ),
                ),
                (
                    "color",
                    models.CharField(
                        blank=True,
                        help_text="The cat's color/pattern",
                        max_length=50,
                        null=True,
                    ),
                ),
                (
                    "weight",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="The cat's weight in kilograms",
                        max_digits=4,
                        null=True,
                    ),
                ),
                (
                    "is_neutered",
                    models.BooleanField(
                        default=False,
                        help_text="Whether the cat has been neutered/spayed",
                    ),
                ),
                (
                    "owner_name",
                    models.CharField(
                        blank=True,
                        help_text="Current owner's name (if adopted)",
                        max_length=100,
                        null=True,
                    ),
                ),
                (
                    "adoption_date",
                    models.DateField(
                        blank=True, help_text="Date when the cat was adopted", null=True
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="Description of the cat's personality and characteristics",
                        null=True,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        help_text="When this record was created",
                    ),
                ),
            ],
            options={
                "verbose_name": "Cat",
                "verbose_name_plural": "Cats",
                "db_table": "cats",
                "ordering": ["id"],
            },
        ),
    ]
