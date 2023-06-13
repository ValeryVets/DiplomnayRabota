from datetime import datetime

from django import forms

from django.contrib import admin
from django.forms import inlineformset_factory

from .models import Subject, Tutor, Student, Lesson, Homework, Task, StudentAnswer
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class FilterForm(forms.Form):#Определяет новый класс формы под названием FilterForm, который наследует от базового класса форм Django.
    SUBJECTS = [
        ('', 'Выберите...'),  # default empty choice
    ]
    SUBJECTS += [(subject.id, subject.name) for subject in Subject.objects.all()]#Инициализирует список SUBJECTS, начиная с пустого варианта выбора, а затем добавляет варианты для каждого объекта Subject в базе данных.
    # Для каждого объекта Subject добавляется кортеж, включающий его id и имя.

    DAYS = [
        (1, 'Понедельник'),
        (2, 'Вторник'),
        (3, 'Среда'),
        (4, 'Четверг'),
        (5, 'Пятница'),
        (6, 'Суббота'),
        (7, 'Воскресенье')
    ]

    subject = forms.ChoiceField(choices=SUBJECTS, required=False)#Создает поле формы под названием 'subject', которое является выпадающим списком с вариантами выбора, определенными в списке SUBJECTS. Параметр 'required=False' означает, что это поле не обязательно для заполнения.
    price = forms.DecimalField(max_digits=6, decimal_places=2, required=False)#Создает поле формы под названием 'price', которое предназначено для ввода десятичных чисел с максимумом 6 цифр, из которых 2 после десятичной точки. Это поле также не является обязательным.
    start_time = forms.TimeField(required=False)#это поля времени, которые также не обязательны для заполнения.
    end_time = forms.TimeField(required=False)
    days_of_week = forms.MultipleChoiceField(choices=DAYS, required=False, widget=forms.CheckboxSelectMultiple)#позволяет выбирать несколько вариантов из списка DAYS. Для отображения этого поля используется виджет CheckboxSelectMultiple.


class TutorAdminForm(forms.ModelForm):#Это класс формы модели Django для модели Tutor.
    class Meta:# это метаданные для формы, которые
        model = Tutor#определяют модель, к которой она привязана (`model = Tutor`)
        fields = '__all__'#она будет использовать (все поля с `fields = '__all__'`)
        widgets = {#какие виджеты использовать для отображения полей (`widgets = {...}`)
            'ordinary_lessons': forms.SelectMultiple(attrs={'required': False}),
            'homeworks': forms.SelectMultiple(attrs={'required': False}),
        }

class StudentAdminForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'
        widgets = {
            'list_tutors': forms.SelectMultiple(attrs={'required': False}),
            'ordinary_lessons': forms.SelectMultiple(attrs={'required': False}),
            'homework': forms.SelectMultiple(attrs={'required': False}),
        }


class EnrollmentForm(forms.Form):
    DAYS_OF_WEEK_CHOICES = (
        (0, 'Понедельник'),
        (1, 'Вторник'),
        (2, 'Среда'),
        (3, 'Четверг'),
        (4, 'Пятница'),
        (5, 'Суббота'),
        (6, 'Воскресенье'),
    )

    tutor_id = forms.IntegerField()#Определение поля `tutor_id`, которое является целочисленным полем.
    start_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    days_of_week = forms.MultipleChoiceField(choices=DAYS_OF_WEEK_CHOICES, required=False, widget=forms.CheckboxSelectMultiple)
    start_time = forms.TimeField(required=False)
    duration = forms.IntegerField(required=False)

class RegisterForm(UserCreationForm):
    username = forms.CharField(
        label='Имя пользователя',
        widget=forms.TextInput(attrs={
            'required': True,
            'pattern': r'^[a-zA-Z0-9@.+-_]+$',
            'title': 'Имя пользователя должно содержать только буквы, цифры и символы @/./+/-/_'
        })
    )
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={
            'required': True,
            'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'title': 'Введите действительный адрес электронной почты'
        })
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'required': True,
            'pattern': r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$',
            'title': 'Пароль должен содержать как минимум 8 символов, включая строчные и прописные буквы и цифры'
        })
    )
    password2 = forms.CharField(
        label='Повторите пароль',
        widget=forms.PasswordInput(attrs={'required': True})
    )
    is_tutor = forms.BooleanField(label='Преподаватель', required=False)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]




class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Имя пользователя')
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Пароль')



class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['exercise', 'answer']
        widgets = {
            'exercise': forms.Textarea(attrs={'class': 'form-control'}),
            'answer': forms.Textarea(attrs={'class': 'form-control'}),
        }

class HomeworkForm(forms.ModelForm):
    class Meta:
        model = Homework
        fields = ['title', 'deadline']
        labels = {
            'title': 'Название',
            'deadline': 'Дедлайн',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

TaskFormSet = inlineformset_factory(Homework, Task, form=TaskForm, extra=1, can_delete=True)


class AnswerForm(forms.ModelForm):
    class Meta:
        model = StudentAnswer
        fields = ['answer']

class TutorProfileForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'ФИО'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    age = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': 'Возраст'}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Контактный телефон'}))
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.Select(attrs={'placeholder': 'Предмет...'}),
    )
    hourly_rate = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': 'Ставка в час'}))
    qualification = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Квалификация'}))
    bio = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Биография'}))

    class Meta:
        model = Tutor
        fields = ['name', 'email', 'age', 'phone', 'subject', 'hourly_rate', 'qualification', 'bio', 'avatar']

class StudentProfileForm(forms.ModelForm):
    avatar = forms.ImageField(widget=forms.FileInput(), required=False)
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'ФИО'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    age = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': 'Возраст'}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Контактный телефон'}))
    parent_phone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Телефон родителя'}))
    parent_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Имя родителя'}))

    class Meta:
        model = Student
        fields = ['name', 'email', 'age', 'phone', 'parent_phone', 'parent_name', 'avatar']


class AvatarForm(forms.ModelForm):
    class Meta:
        model = Tutor
        fields = ['avatar']