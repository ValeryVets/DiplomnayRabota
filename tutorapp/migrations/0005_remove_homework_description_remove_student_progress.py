# Generated by Django 4.2.1 on 2023-05-28 19:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tutorapp', '0004_student_avatar_tutor_avatar'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='homework',
            name='description',
        ),
        migrations.RemoveField(
            model_name='student',
            name='progress',
        ),
    ]
