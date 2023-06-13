from django.urls import path#импортирует функцию `path` из модуля `django.urls`, которая используется для определения маршрутов URL в Django.
from . import views#импортирует модуль `views.py`, в котором содержатся функции обработки запросов.

app_name = 'tutorapp'#задает пространство имен для URL-шаблонов этого приложения. Это позволяет ссылаться на URL-шаблоны из этого приложения в шаблонах и функциях `reverse()` Django.

urlpatterns = [#Это определяет список URL-шаблонов для этого Django приложения.
    path('', views.welcome, name='welcome'),  # заменили 'main' на 'welcome' пользователь переходит по этому URL, вызывается функция `welcome` из `views.py`.
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('main/', views.main, name='main'),# добавили новый маршрут для главной страницы
    path('api/tutor/<int:tutor_id>/', views.tutor_detail_api, name='tutor_detail_api'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('tutor_dashboard/', views.tutor_dashboard, name='tutor_dashboard'),
    path('accept_request/<str:student_name>/<str:subject_name>/', views.accept_request, name='accept_request'),
    path('decline_request/<str:student_name>/<str:subject_name>/', views.decline_request, name='decline_request'),
    path('homework/create/<int:lesson_id>/', views.create_homework, name='create_homework'),
    path('homework/<int:homework_id>/', views.homework_page, name='homework_page'),
    path('check_homework/<int:pk>', views.check_homework, name='check_homework'),
    path('update_avatar/', views.update_avatar, name='update_avatar'),
]
#`name=...`: Это имена URL-шаблонов, которые можно использовать для ссылки на эти URL из шаблонов и функций `reverse()` Django.
#определяют другие URL-шаблоны. Первый аргумент каждой функции `path` - это шаблон URL. Второй аргумент - функция обработчика, которая вызывается, когда пользователь переходит по соответствующему URL.
# Некоторые из этих URL-шаблонов используют переменные (например, `<int:tutor_id>`, `<str:student_name>`, `<int:lesson_id>` и т.д.), которые извлекаются из URL и передаются в функцию обработчика.