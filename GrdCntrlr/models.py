from django.db import models

class DataBase(models.Model):
    login = models.CharField('Логин', max_length=200)
    password = models.CharField('Пароль', max_length=200)
    checkbox = models.BooleanField('Запоминать')
    subjects = models.TextField(default='')

class A(models.Model):
    agrade = models.CharField('Новая Оценка', max_length=3)
    invis_indx = models.CharField('Индекс agrade', max_length=3)