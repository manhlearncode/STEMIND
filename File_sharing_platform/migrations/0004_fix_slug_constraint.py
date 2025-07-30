# Generated manually to fix slug constraint issue

from django.db import migrations, models
from django.utils.text import slugify


def populate_slugs(apps, schema_editor):
    Category = apps.get_model('File_sharing_platform', 'Category')
    File = apps.get_model('File_sharing_platform', 'File')
    
    # Populate category slugs
    for category in Category.objects.all():
        if not category.slug:
            base_slug = slugify(category.category_name)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exclude(id=category.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            category.slug = slug
            category.save()
    
    # Populate file slugs
    for file_obj in File.objects.all():
        if not file_obj.slug:
            base_slug = slugify(file_obj.title)
            slug = base_slug
            counter = 1
            while File.objects.filter(slug=slug).exclude(id=file_obj.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            file_obj.slug = slug
            file_obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ('File_sharing_platform', '0003_file_download_count_alter_file_file_thumbnail_and_more'),
    ]

    operations = [
        # First add slug fields without unique constraint
        migrations.AddField(
            model_name='category',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='file',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, null=True),
        ),
        
        # Populate slugs
        migrations.RunPython(populate_slugs),
        
        # Make slug fields not null
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(max_length=255),
        ),
        migrations.AlterField(
            model_name='file',
            name='slug',
            field=models.SlugField(max_length=255),
        ),
        
        # Add unique constraints
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='file',
            name='slug',
            field=models.SlugField(max_length=255, unique=True),
        ),
        
        # Add other fields from the original migration
        migrations.AddField(
            model_name='file',
            name='file_size',
            field=models.PositiveIntegerField(default=0, help_text='File size in bytes'),
        ),
        migrations.AddField(
            model_name='file',
            name='file_type',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='file',
            name='tags',
            field=models.CharField(blank=True, help_text='Comma-separated tags', max_length=500),
        ),
        
        # Add indexes
        migrations.AddIndex(
            model_name='file',
            index=models.Index(fields=['file_status', '-created_at'], name='File_sharin_file_st_4c52ce_idx'),
        ),
        migrations.AddIndex(
            model_name='file',
            index=models.Index(fields=['category', '-created_at'], name='File_sharin_categor_accf82_idx'),
        ),
        migrations.AddIndex(
            model_name='file',
            index=models.Index(fields=['author', '-created_at'], name='File_sharin_author__629f9a_idx'),
        ),
        
        # Update model options
        migrations.AlterModelOptions(
            name='category',
            options={
                'ordering': ['category_name'],
                'verbose_name_plural': 'Categories',
            },
        ),
    ] 