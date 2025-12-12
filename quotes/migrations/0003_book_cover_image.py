# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quotes', '0002_book_review'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='book',
            name='cover_image_url',
        ),
        migrations.AddField(
            model_name='book',
            name='cover_image',
            field=models.ImageField(blank=True, null=True, upload_to='book_covers/'),
        ),
    ]

