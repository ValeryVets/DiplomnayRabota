from django.contrib import admin#Это импортирует модуль администратора Django, который позволяет создавать интерфейс администратора для моделей вашего приложения.
from .models import Tutor, Student, Lesson, Homework, Enrollment, Subject, Task, StudentAnswer#Это импортирует все указанные модели из файла models.py текущего Django-приложения.


class TutorAdmin(admin.ModelAdmin):
    exclude = ('ordinary_lessons', 'homeworks',)
#Это объявления классов администраторов для моделей Tutor и Student. Эти классы наследуются от `admin.ModelAdmin` и позволяют настроить поведение интерфейса администратора для этих моделей.
#это настройки, которые определяют, какие поля будут исключены из формы редактирования модели в интерфейсе администратора.
class StudentAdmin(admin.ModelAdmin):
    exclude = ('list_tutors', 'ordinary_lessons', 'homework',)

admin.site.register(Tutor, TutorAdmin)#Это регистрация моделей Tutor и Student в интерфейсе администратора с использованием настроенных классов администраторов `TutorAdmin` и `StudentAdmin`.
admin.site.register(Student, StudentAdmin)
admin.site.register(Lesson)#Это регистрация остальных моделей в интерфейсе администратора. Здесь не используются специальные классы администраторов, поэтому будут использоваться настройки по умолчанию.
admin.site.register(Homework)
admin.site.register(Enrollment)
admin.site.register(Subject)
admin.site.register(Task)
admin.site.register(StudentAnswer)