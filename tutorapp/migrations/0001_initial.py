# Generated by Django 4.2.1 on 2023-05-28 11:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Homework',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('deadline', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, null=True)),
                ('age', models.IntegerField()),
                ('phone', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=254)),
                ('progress', models.TextField()),
                ('parent_phone', models.CharField(max_length=20)),
                ('parent_name', models.CharField(max_length=100)),
                ('homework', models.ManyToManyField(related_name='students', to='tutorapp.homework')),
                ('user', models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Tutor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('age', models.IntegerField()),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=20)),
                ('hourly_rate', models.DecimalField(decimal_places=2, max_digits=6)),
                ('qualification', models.TextField()),
                ('bio', models.TextField()),
                ('homeworks', models.ManyToManyField(related_name='tutors', to='tutorapp.homework')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tutorapp.subject')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exercise', models.TextField()),
                ('answer', models.TextField()),
                ('homework', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='tutorapp.homework')),
            ],
        ),
        migrations.CreateModel(
            name='StudentAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.TextField()),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tutorapp.student')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tutorapp.task')),
            ],
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, null=True)),
                ('description', models.TextField(null=True)),
                ('date', models.DateTimeField()),
                ('duration', models.PositiveIntegerField()),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tutorapp.student')),
                ('tutor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tutorapp.tutor')),
            ],
        ),
        migrations.AddField(
            model_name='homework',
            name='lesson',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='tutorapp.lesson'),
        ),
        migrations.CreateModel(
            name='Enrollment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('desired_date', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('duration', models.PositiveIntegerField()),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tutorapp.student')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tutorapp.subject')),
                ('tutor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tutorapp.tutor')),
            ],
        ),
    ]
