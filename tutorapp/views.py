import json
from collections import defaultdict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import ExpressionWrapper, Func, CharField, F
from django.forms import inlineformset_factory, formset_factory
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.views.generic import DetailView
from django.urls import reverse


from .models import Lesson, Homework, Tutor, Student, Enrollment, Subject, Task, StudentAnswer
from .forms import FilterForm, RegisterForm, LoginForm, EnrollmentForm, HomeworkForm, TaskForm, AnswerForm, \
    TutorProfileForm, AvatarForm, StudentProfileForm
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, HttpResponseRedirect
from django.utils import timezone
from datetime import datetime, timedelta, date


def welcome(request):
    return render(request, 'welcome.html')


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')

            # Check if the user is a tutor
            if form.cleaned_data.get('is_tutor'):#Проверка, выбрал ли пользователь в форме регистрации опцию "Преподаватель".
                Tutor.objects.create(user=user, email=email)#Создание нового объекта `Tutor`, привязанного к новому пользователю.
            else:
                Student.objects.create(user=user, email=email)#создается новый объект `Student`, привязанный к новому пользователю.

            # Update the request user and log them in
            request.user = user#Обновление текущего пользователя в объекте запроса.
            login(request, user)#Залогинивание пользователя.
            return redirect('tutorapp:main')#Перенаправление пользователя на главную страницу приложения после успешной регистрации.
    else:
        form = RegisterForm()#инициализируется пустая форма регистрации.
    return render(request, 'register.html', {'form': form})#и отрисовывается страница регистрации с этой пустой формой.



def login_view(request):#Определение функции `login_view`, которая принимает `request` (HTTP-запрос) в качестве аргумента. Эта функция обрабатывает как GET, так и POST-запросы на авторизацию.
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('tutorapp:main')  # assuming you have a route named 'home'
            else:
                messages.error(request, "Invalid username or password")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)#Выход текущего пользователя из системы.
    return redirect('tutorapp:main')  #Перенаправление пользователя на главную страницу приложения после выхода из системы.


def main(request):  # Определение функции main для обработки запроса.
    form = FilterForm()  # Инициализация формы фильтра без данных.
    tutors = Tutor.objects.all()  # Получение всех объектов `Tutor` из базы данных.
    enrollment_form = EnrollmentForm()  # Инициализация формы записи на занятия без данных.

    if request.method == 'POST':  # Проверка, является ли метод запроса POST.
        if 'filter_button' in request.POST:  # Проверка, была ли нажата кнопка фильтра.
            form = FilterForm(request.POST)  # Инициализация формы фильтра с данными из POST-запроса.
            if form.is_valid():  # Проверка валидности данных формы.
                # Получение введенного пользователем предмета и цены из очищенных данных формы.
                subject = form.cleaned_data.get('subject')
                price = form.cleaned_data.get('price')
                # Инициализация пустого словаря для хранения времени начала и конца для каждого дня недели.
                times_for_days = {}
                for day in range(1, 8):  # Проход по всем дням недели (от 1 до 7 включительно).
                    # Формирование имени ключа для извлечения времени начала и окончания из данных POST-запроса для данного дня.
                    start_time_name = f'start_time_id_days_of_week_{day}'
                    end_time_name = f'end_time_id_days_of_week_{day}'
                    # Получение строки времени начала и окончания из данных POST-запроса.
                    start_time_str = request.POST.get(start_time_name)
                    end_time_str = request.POST.get(end_time_name)
                    # Если оба значения существуют и не пусты, то преобразовать строки в объекты времени.
                    if start_time_str and end_time_str:
                        start_time = datetime.strptime(start_time_str, "%H:%M").time()
                        end_time = datetime.strptime(end_time_str, "%H:%M").time()
                        times_for_days[day] = (start_time, end_time)

                # Фильтрация репетиторов по предмету и цене, если они указаны.
                if subject:
                    tutors = tutors.filter(subject=subject)
                if price:
                    tutors = tutors.filter(hourly_rate__lte=price)

                exclude_tutor_ids = set()  # Инициализация множества для идентификаторов репетиторов, которые следует исключить.

                # Проверка каждого репетитора на возможность урока в выбранное время.
                for tutor in tutors:
                    lessons = Lesson.objects.filter(tutor=tutor)

                    for lesson in lessons:
                        lesson_day = lesson.date.weekday()
                        if lesson_day in times_for_days:
                            lesson_start_time = lesson.date.time()
                            lesson_end_time = (datetime.combine(date.min, lesson_start_time) + timedelta(
                                minutes=lesson.duration)).time()
                            filter_start_time, filter_end_time = times_for_days[lesson_day]

                            # Если время пересекается, исключить репетитора из списка.
                            if not (lesson_end_time <= filter_start_time or lesson_start_time >= filter_end_time):
                                exclude_tutor_ids.add(tutor.id)
                                break

                tutors = tutors.exclude(id__in=exclude_tutor_ids)  # Исключение репетиторов по идентификаторам.
            else:  # Если форма не валидна, перенаправить на главную страницу с сообщением об ошибке.
                messages.error(request, 'You must be logged in as a student to enroll.')
                return redirect('tutorapp:main')

        elif 'enrollment_button' in request.POST:  # Проверка, была ли нажата кнопка записи на занятия.
            enrollment_form = EnrollmentForm(request.POST)  # Инициализация формы записи на занятия с данными из POST-запроса.
            if enrollment_form.is_valid():  # Проверка валидности данных формы.
                # Получение введенных пользователем данных из очищенных данных формы.
                tutor_id = enrollment_form.cleaned_data.get('tutor_id')
                start_date = enrollment_form.cleaned_data.get('start_date')
                end_date = enrollment_form.cleaned_data.get('end_date')
                days_of_week = [int(day) for day in enrollment_form.cleaned_data.get('days_of_week')]

                tutor = get_object_or_404(Tutor, pk=tutor_id)  # Получение репетитора по id или возврат 404 ошибки, если репетитора не существует.

                student = Student.objects.filter(user=request.user).first()  # Получение студента, соответствующего текущему пользователю.
                if student is None:  # Если студент не найден, перенаправить на главную страницу с сообщением об ошибке.
                    messages.error(request, 'You must be logged in as a student to enroll.')
                    return redirect('tutorapp:main')

                # Создание объектов записи на занятия для каждого дня недели в выбранном диапазоне дат.
                delta = timedelta(days=1)
                current_date = start_date
                while current_date <= end_date:
                    if current_date.weekday() in days_of_week:
                        start_time_str = request.POST.get(f'start_id_days_of_week_{current_date.weekday()}')
                        duration_str = request.POST.get(f'duration_id_days_of_week_{current_date.weekday()}')

                        if not start_time_str or not duration_str:
                            messages.error(request, f'You must specify a start time and duration for {current_date}.')
                            return redirect('tutorapp:main')

                        start_time = datetime.strptime(start_time_str, "%H:%M").time()
                        duration = int(duration_str)

                        desired_datetime = timezone.make_aware(datetime.combine(current_date, start_time))
                        end_time = (datetime.combine(current_date, start_time) + timedelta(minutes=duration)).time()
                        # Проверка, свободен ли репетитор в данное время.
                        lessons = Lesson.objects.filter(tutor=tutor, date__day=current_date.day,
                                                        date__time__range=(start_time, end_time))
                        if lessons.exists():
                            messages.error(request,
                                           f'Tutor is not available on {current_date} from {start_time} to {end_time}.')
                            return redirect('tutorapp:main')

                        # Создание объекта записи на занятия.
                        Enrollment.objects.create(
                            student=student,
                            tutor=tutor,
                            subject=tutor.subject,
                            desired_date=desired_datetime,
                            duration=duration
                        )
                    current_date += delta

                # Перенаправление на главную страницу с сообщением об успехе.
                messages.success(request, 'You have successfully enrolled.')
                return redirect('tutorapp:main')
            else:  # Если форма не валидна, перенаправить на главную страницу с сообщением об ошибке.
                messages.error(request, 'You must be logged in as a student to enroll.')

    # Рендеринг главной страницы с передачей контекста в шаблон.
    return render(request, 'Main.html', {'form': form, 'tutors': tutors, 'enrollment_form': enrollment_form})





def tutor_detail_api(request, tutor_id):
    tutor = Tutor.objects.get(pk=tutor_id)  # Получение объекта репетитора по первичному ключу (id).
    data = {  # Формирование словаря данных о репетиторе.
        "name": tutor.name,
        "email": tutor.email,
        "age": tutor.age,
        "phone": tutor.phone,
        "subject": str(tutor.subject),
        "qualification": tutor.qualification,
        "bio": tutor.bio,
        "avatar": tutor.avatar.url if tutor.avatar else None,  # Если у репетитора есть аватар, добавляем его URL, иначе None.
    }
    return JsonResponse(data)  # Возвращение JSON ответа с данными о репетиторе.

@login_required  # Декоратор, требующий авторизации пользователя.
def student_dashboard(request):
    student = Student.objects.filter(user=request.user).first()  # Получение объекта студента, связанного с текущим пользователем.
    if student is None:  # Если студент не найден, производится перенаправление на страницу приветствия.
        return redirect('tutorapp:welcome')

    if request.method == 'POST':  # Обработка POST-запроса.
        form = StudentProfileForm(request.POST, request.FILES, instance=student)  # Создание формы с данными из запроса и текущим экземпляром студента.
        if form.is_valid():  # Проверка валидности формы.
            form.save()  # Сохранение формы.
    else:  # Если запрос не POST, создается пустая форма.
        form = StudentProfileForm(instance=student)

    days_mapping = {  # Создание словаря, сопоставляющего числа дней недели с их названиями.
        1: 'Понедельник',
        2: 'Вторник',
        3: 'Среда',
        4: 'Четверг',
        5: 'Пятница',
        6: 'Суббота',
        7: 'Воскресенье'
    }

    current_week = datetime.now().isocalendar()[1]  # Получение текущей недели.

    lessons = Lesson.objects.filter(student=student)
    tutors = Tutor.objects.filter(lesson__in=lessons).distinct()  # Получение уникальных репетиторов, которые ведут эти уроки.
    current_week = datetime.now().isocalendar()[1]
    next_week = current_week + 1
    lessons = [lesson for lesson in lessons if current_week <= lesson.date.isocalendar()[1] <= next_week]  # Фильтрация уроков по текущей и следующей неделям.
    students = Student.objects.filter(lesson__in=lessons).distinct()  # Получение уникальных студентов, участвующих в этих уроках.

    lessons_weekday = defaultdict(list)  # Создание словаря, где ключи - дни недели, а значения - списки уроков.
    for lesson in lessons:
        weekday = days_mapping[lesson.date.weekday() + 1]  # Преобразование номера дня недели в его название.
        date = lesson.date.strftime('%d.%m.%Y')  # Преобразование даты урока в строку.
        weekday_key = f'{weekday} {date}'  # Создание ключа для словаря lessons_weekday.
        start_time = lesson.date.strftime('%H:%M')  # Преобразование времени начала урока в строку.
        end_time = (datetime.strptime(start_time, '%H:%M') + timedelta(minutes=lesson.duration)).strftime('%H:%M')  # Вычисление времени окончания урока.
        title = lesson.title.replace(' lesson', '')  # Удаление 'lesson' из названия урока.
        lesson_info = {'start_time': start_time,
                       'end_time': end_time,
                       'title': title}  # Создание словаря информации об уроке.
        lessons_weekday[weekday_key].append(lesson_info)  # Добавление информации об уроке в список уроков для данного дня.

    days_order = {v: k for k, v in days_mapping.items()}  # Создание словаря, сопоставляющего названия дней недели с их числами.

    sorted_lessons_weekday = {weekday: sorted(lessons, key=lambda x: x['start_time']) for weekday, lessons in
                              lessons_weekday.items()}  # Сортировка уроков каждого дня по времени начала.

    sorted_lessons_weekday = dict(sorted(sorted_lessons_weekday.items(),
                                         key=lambda item: (days_order[item[0].split()[0]], item[0].split()[1])))  # Сортировка дней по порядку в неделе и по дате.

    lessons = [{
        'id': lesson.id,
        'formatted_date': lesson.date.strftime('%d.%m.%Y в %H:%M'),
        'duration': lesson.duration,
        'tutor_name': lesson.tutor.name,
        'title': lesson.title.replace(' lesson', ''),
        'homework': Homework.objects.filter(lesson=lesson).first(),
    } for lesson in lessons]  # Преобразование списка уроков в список словарей с нужной информацией об уроках.

    return render(request, 'StudentLk.html', {  # Отображение страницы "личный кабинет студента" и передача в шаблон необходимых данных.
        'student': student,
        'lessons': lessons,
        'tutors': tutors,
        'sorted_lessons_weekday': sorted_lessons_weekday,
        'form': form,
    })



@login_required  # Декоратор, требующий авторизации пользователя.
def tutor_dashboard(request):
    tutor = Tutor.objects.filter(user=request.user).first()  # Получение объекта репетитора, связанного с текущим пользователем.
    if tutor is None:  # Если репетитор не найден, производится перенаправление на страницу приветствия.
        return redirect('tutorapp:welcome')

    if request.method == 'POST':  # Обработка POST-запроса.
        form = TutorProfileForm(request.POST, request.FILES, instance=tutor)  # Создание формы с данными из запроса и текущим экземпляром репетитора.
        if form.is_valid():  # Проверка валидности формы.
            form.save()  # Сохранение формы.
    else:  # Если запрос не POST, создается пустая форма.
        form = TutorProfileForm(instance=tutor)

    enrollments = Enrollment.objects.filter(tutor=tutor)  # Получение списка записей на уроки для данного репетитора.
    grouped_enrollments = defaultdict(list)  # Создание словаря, где ключи - пары (id студента, id предмета), а значения - списки записей.

    for enrollment in enrollments:
        key = (enrollment.student.id, enrollment.subject.id)  # Формирование ключа.
        grouped_enrollments[key].append(enrollment)  # Добавление записи в соответствующий список.

    display_enrollments = []  # Список для отображения записей.
    days_mapping = {  # Создание словаря, сопоставляющего числа дней недели с их названиями.
        1: 'Понедельник',
        2: 'Вторник',
        3: 'Среда',
        4: 'Четверг',
        5: 'Пятница',
        6: 'Суббота',
        7: 'Воскресенье'
    }

    for key, group in grouped_enrollments.items():  # Обработка каждой группы записей.
        student_name = group[0].student.name  # Получение имени студента.
        subject_name = group[0].subject.name  # Получение названия предмета.
        start_date = min(enrollment.desired_date.date() for enrollment in group)  # Получение даты первой записи.
        end_date = max(enrollment.desired_date.date() for enrollment in group)  # Получение даты последней записи.

        days_and_times = {}  # Словарь для дней и времени проведения уроков.
        for enrollment in group:  # Обработка каждой записи в группе.
            weekday = days_mapping[enrollment.desired_date.weekday() + 1]  # Получение дня недели.
            time = enrollment.desired_date.strftime('%H:%M')  # Получение времени начала урока.
            duration = enrollment.duration  # Получение продолжительности урока.
            if weekday not in days_and_times:  # Если такого дня еще нет в словаре, добавляем его.
                days_and_times[weekday] = (time, duration)

        display_enrollments.append({  # Добавление информации об записях в список для отображения.
            'student_name': student_name,
            'subject_name': subject_name,
            'start_date': start_date,
            'end_date': end_date,
            'days_and_times': list(days_and_times.items()),
        })

    lessons = Lesson.objects.filter(tutor=tutor)  # Получение списка уроков данного репетитора.
    current_week = datetime.now().isocalendar()[1]  # Получение номера текущей недели.
    next_week = current_week + 1  # Получение номера следующей недели.
    lessons = [lesson for lesson in lessons if current_week <= lesson.date.isocalendar()[1] <= next_week]  # Фильтрация уроков по дате.
    students = Student.objects.filter(lesson__in=lessons).distinct()  # Получение списка уникальных студентов, имеющих уроки.

    lessons_weekday = defaultdict(list)  # Создание словаря, где ключи - дни недели, а значения - списки уроков.
    for lesson in lessons:
        weekday = days_mapping[lesson.date.weekday() + 1]  # Преобразование номера дня недели в его название.
        date = lesson.date.strftime('%d.%m.%Y')  # Преобразование даты урока в строку.
        weekday_key = f'{weekday} {date}'  # Создание ключа для словаря lessons_weekday.
        start_time = lesson.date.strftime('%H:%M')  # Преобразование времени начала урока в строку.
        end_time = (datetime.strptime(start_time, '%H:%M') + timedelta(minutes=lesson.duration)).strftime('%H:%M')  # Вычисление времени окончания урока.
        title = lesson.title.replace(' lesson', '')  # Удаление 'lesson' из названия урока.
        lesson_info = {'start_time': start_time,
                       'end_time': end_time,
                       'title': title}  # Создание словаря информации об уроке.
        lessons_weekday[weekday_key].append(lesson_info)  # Добавление информации об уроке в список уроков для данного дня.

    days_order = {v: k for k, v in days_mapping.items()}  # Создание словаря, сопоставляющего названия дней недели с их числами.

    sorted_lessons_weekday = {weekday: sorted(lessons, key=lambda x: x['start_time']) for weekday, lessons in
                              lessons_weekday.items()}  # Сортировка уроков каждого дня по времени начала.

    sorted_lessons_weekday = dict(sorted(sorted_lessons_weekday.items(),
                                         key=lambda item: (days_order[item[0].split()[0]], item[0].split()[1])))  # Сортировка дней по порядку в неделе и по дате.

    lessons_data = []  # Список для информации об уроках.
    for lesson in lessons:  # Обработка каждого урока.
        homework = Homework.objects.filter(lesson=lesson).first()  # Получение домашнего задания для урока.
        tasks = []  # Список заданий.
        if homework:  # Если есть домашнее задание.
            tasks = [{  # Добавление информации о задании в список.
                'exercise': task.exercise,
                'answer': task.answer,
                'student_answer': StudentAnswer.objects.filter(task=task).first()
            } for task in homework.tasks.all()]

        lesson_data = {  # Создание словаря с информацией об уроке.
            'id': lesson.id,
            'formatted_date': lesson.date.strftime('%d.%m.%Y в %H:%M'),
            'duration': lesson.duration,
            'student_name': lesson.student.name,
            'title': lesson.title.replace(' lesson', ''),
            'homework': homework,
            'tasks': tasks,
        }

        lessons_data.append(lesson_data)  # Добавление информации об уроке в список.

    # Возвращение страницы с информацией о репетиторе, его учениках, уроках и формой для редактирования профиля.
    return render(request, 'TutorLk.html', {
        'tutor': tutor,
        'display_enrollments': display_enrollments,
        'lessons': lessons_data,
        'students': students,
        'sorted_lessons_weekday': sorted_lessons_weekday,
        'form': form,
    })

# Эта функция вызывается при подтверждении заявки студента на обучение.
@require_POST
def accept_request(request, student_name, subject_name):
    tutor = Tutor.objects.filter(user=request.user).first()  # Получение текущего пользователя.
    # Получение заявок студента на обучение.
    enrollments = Enrollment.objects.filter(tutor=tutor, student__name=student_name, subject__name=subject_name)
    for enrollment in enrollments:  # Обработка каждой заявки.
        # Создание урока на основе информации из заявки.
        Lesson.objects.create(
            title=f"{enrollment.subject.name} lesson",
            description="",
            tutor=tutor,
            student=enrollment.student,
            date=enrollment.desired_date,
            duration=enrollment.duration
        )
    enrollments.delete()  # Удаление заявок после создания уроков.
    # Перенаправление на страницу репетитора.
    return HttpResponseRedirect(reverse('tutorapp:tutor_dashboard'))

# Эта функция вызывается при отказе от заявки студента на обучение.
@require_POST
def decline_request(request, student_name, subject_name):
    tutor = Tutor.objects.filter(user=request.user).first()  # Получение текущего пользователя.
    # Удаление заявок студента на обучение.
    Enrollment.objects.filter(tutor=tutor, student__name=student_name, subject__name=subject_name).delete()
    # Перенаправление на страницу репетитора.
    return HttpResponseRedirect(reverse('tutorapp:tutor_dashboard'))

# Эта функция вызывается при создании домашнего задания для урока.
def create_homework(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)  # Получение урока по идентификатору.
    if request.method == 'POST':  # Если была отправлена форма.
        form = HomeworkForm(request.POST)  # Создание формы на основе отправленных данных.
        if form.is_valid():  # Если форма корректна.
            homework = form.save(commit=False)  # Сохранение формы без коммита.
            homework.lesson = lesson  # Привязка домашнего задания к уроку.
            homework.save()  # Сохранение домашнего задания.

            tasks_data = json.loads(request.POST['tasks'])  # Получение данных о заданиях.

            for task_data in tasks_data:  # Обработка каждого задания.
                task = Task(homework=homework, **task_data)  # Создание задания на основе данных.
                task.save()  # Сохранение задания.

            # Перенаправление на страницу репетитора.
            return redirect('tutorapp:tutor_dashboard')
    else:
        form = HomeworkForm()  # Создание пустой формы для домашнего задания.

    # Возвращение страницы с формой для создания домашнего задания.
    return render(request, 'create_homework.html', {'form': form})

# Эта функция вызывается при просмотре домашнего задания.
def homework_page(request, homework_id):
    homework = Homework.objects.get(id=homework_id)  # Получение домашнего задания по идентификатору.
    tasks = Task.objects.filter(homework=homework)  # Получение заданий для домашнего задания.
    student = request.user.student  # Получение текущего студента.

    if request.method == 'POST':  # Если была отправлена форма.
        for task in tasks:  # Обработка каждого задания.
            # Получение ответа студента из формы.
            answer_text = request.POST.get('task_answer_' + str(task.id))
            answer_file = request.FILES.get('task_file_' + str(task.id))
            if answer_text or answer_file:  # Если студент отправил ответ.
                # Создание объекта ответа студента на основе отправленных данных.
                StudentAnswer.objects.create(task=task, student=student, answer=answer_text, image=answer_file)

        # Отметка домашнего задания как выполненного студентом.
        homework.completed.add(student)

        # Перенаправление на страницу студента.
        return redirect('tutorapp:student_dashboard')

    # Возвращение страницы с домашним заданием.
    return render(request, 'homework_page.html', {'homework': homework, 'tasks': tasks})

# Эта функция вызывается при обновлении аватара студента.
@login_required
def update_avatar(request):
    if request.method == 'POST':  # Если была отправлена форма.
        try:   # Если пользователь студент является преподавателем.
            form = AvatarForm(request.POST, request.FILES, instance=request.user.tutor)  # Создание формы на основе отправленных данных.
        except:  # Если пользователь студент.
            form = AvatarForm(request.POST, request.FILES, instance=request.user.student)  # Создание формы на основе отправленных данных.

        if form.is_valid():  # Если форма корректна.
            form.save()  # Сохранение формы.
            return JsonResponse({'success': True})  # Возвращение успешного ответа.
    return JsonResponse({'success': False})  # Возвращение неуспешного ответа.

# Эта функция вызывается при проверке домашнего задания репетитором.
@login_required
def check_homework(request, pk):
    homework = get_object_or_404(Homework, pk=pk)  # Получение домашнего задания по идентификатору.
    homework.checked = True  # Отметка домашнего задания как проверенного.
    homework.save()  # Сохранение домашнего задания.
    # Перенаправление на страницу репетитора.
    return redirect('tutorapp:tutor_dashboard')
