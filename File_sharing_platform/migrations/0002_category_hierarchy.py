# Generated manually for category hierarchy migration

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("File_sharing_platform", "0001_initial"),
    ]

    operations = [
        # Step 1: Add new fields to Category model
        migrations.AddField(
            model_name="category",
            name="name",
            field=models.CharField(default="", max_length=255),
        ),
        migrations.AddField(
            model_name="category",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="children",
                to="File_sharing_platform.category",
            ),
        ),
        migrations.AddField(
            model_name="category",
            name="description",
            field=models.TextField(blank=True, null=True),
        ),
        
        # Step 2: Add ManyToManyField to File model
        migrations.AddField(
            model_name="file",
            name="categories",
            field=models.ManyToManyField(
                related_name="files", to="File_sharing_platform.category"
            ),
        ),
        
        # Step 3: Remove old category field from File model
        migrations.RemoveField(
            model_name="file",
            name="category",
        ),
        
        # Step 4: Remove old category_name field from Category model
        migrations.RemoveField(
            model_name="category",
            name="category_name",
        ),
        
        # Step 5: Add unique_together constraint
        migrations.AlterUniqueTogether(
            name="category",
            unique_together={("name", "parent")},
        ),
    ] 