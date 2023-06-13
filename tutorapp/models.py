from django.db import models
from django.contrib.auth.models import User

class Homework(models.Model):
    lesson = models.OneToOneField("Lesson", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    deadline = models.DateField()
    completed = models.ManyToManyField("Student", related_name='completed_homeworks')
    checked = models.BooleanField(default=False)

    def __str__(self):
        return self.title
class Subject(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.name

class Tutor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, default="Нет имени")
    age = models.IntegerField(null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True)
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    qualification = models.TextField(null=True)
    homeworks = models.ManyToManyField(Homework, related_name='tutors', null=True)
    bio = models.TextField(null=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)


    def __str__(self):
        return self.name if self.name else "No Name"

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True)
    name = models.CharField(max_length=100, default="Нет имени")
    age = models.IntegerField(null=True)
    phone = models.CharField(max_length=20, null=True)
    email = models.EmailField()
    homework = models.ManyToManyField(Homework, related_name='students')
    parent_phone = models.CharField(max_length=20, null=True)
    parent_name = models.CharField(max_length=100, null=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)


    def __str__(self):
        return self.name if self.name else "No Name"


class Lesson(models.Model):
    title = models.CharField(max_length=200, null=True)
    description = models.TextField(null=True)
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateTimeField()
    duration = models.PositiveIntegerField()  # in minutes

    def __str__(self):
        return f"{self.tutor.name} - {self.student.name} - {self.date}"

class Task(models.Model):
    homework = models.ForeignKey(Homework, related_name='tasks', on_delete=models.CASCADE)
    exercise = models.TextField()
    answer = models.TextField()
    # Add more fields if needed


class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    desired_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    duration = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.student.name} - {self.tutor.name} - {self.subject.name} - {self.desired_date}"


class StudentAnswer(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    answer = models.TextField()
    image = models.ImageField(upload_to='student_answers/', blank=True, null=True)

