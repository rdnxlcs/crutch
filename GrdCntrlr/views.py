from http import cookies
from operator import index
from django.shortcuts import redirect, render, HttpResponse
from .forms import DataBaseForm, AForm
from .models import DataBase, A
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
import time 
import jsonpickle as json
import math
import numpy as np
from itertools import groupby
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt

# ----------Объекты базы данных----------
class Grade: # Объект оценка
    def __init__(self, grade, coef, ix, agrade):
        self.grade = grade # Балл   
        self.coef = coef # Коэффицент
        self.ix = ix # Индек оценки - номер оценки в строке предмета
        self.agrade = agrade # Искусственный балл - заранее исправленная оценка пользователем (а-оценка)

class Sub_Grades: # Объект предмет
    def __init__(self, subject, grades, mean, amean, target, graph):
        self.subject = subject # Название предмета
        self.grades = grades # Массив с оценками (состоит из объектов оценка)
        self.mean = mean # Средняя арифметическая оценка по предмету
        self.amean = amean # Средняя арифметическая оценка по предмету с учетом a-оценок
        self.target = target # Цель
        self.graph = graph
# -------------------- 

# ----------Функции обработки информации----------
def convert(s, nmbr, data, subject): # Конвертирование ячейки оценки из HTML кода элжура в объект Grade (оценка), s - строка из HTML кода, nmbr - порядковый номер оценки
    temp = Grade(0, 0, nmbr, 0)
    newdata = json.decode(data.subjects)
    if '✕' in s: # Проверка на наличие коэффицента в ячейке оценки
        try: # Содержимое ячейки может быть преобразованно в число
            temp.grade = int(s[:-2])
            temp.coef = int(s[-1])
            temp.ix = str(nmbr) + '_' + str(subject) # Индекс оценки: порядковый номер и название предмета
            try:
                temp.agrade = newdata[sbjctix(newdata, subject)].grades[int(nmbr)].agrade
            except:
                temp.agrade = temp.grade
        except: # Иначе вернуть объект оценки без содержимого (кроме индекса)
            return Grade(None, None, nmbr, None)
    else: # При отсутствии 'x' в ячейке оценки коэффицент 1

        try:
            temp.grade = int(s)
            temp.coef = 1
            temp.ix = str(nmbr) + '_' + str(subject)
            try:
                temp.agrade = newdata[sbjctix(newdata, subject)].grades[int(nmbr)].agrade
            except:
                temp.agrade = temp.grade     
        except:
            return Grade(None, None, nmbr, None)
    print(temp.ix)
    return temp # Вернуть объект Grade (оценка) 

def get_subjects(browser): # Взятие названий предметов из HTML кода элжура, browser - драйвер на котором работает selenium
    els = browser.find_elements(By.XPATH, '//div[@class="text-overflow lhCell offset16"]') # Поиск ячеек необходимого типа
    subjects = []
    for el in els:
        subjects.append(el.text) # Занести названия предметов в массив
    return subjects # Вернуть массив с названиями предметов

def get_grades(subject, browser, data): # Взяие оценок из строки предмета, subject - название предмета 
    els = browser.find_elements(By.XPATH, '//div[@id="g0_marks"]//div[@name="' + subject + '"]//div[@class="cell-data"]') # Поиск необходимой строки
    grades = []
    for el in els:
        if grades != []: # Если массив с оценками не пустой
            grades.append(convert(el.text, grades.index(grades[-1]) + 1, data, subject)) # Занести объект Grades (оценка) в массив
        else: # Иначе порядковый номер оценки 0
            grades.append(convert(el.text, 0, data, subject))
        if grades[-1].grade == None and grades[-1].coef == None: # Удаление пустых оценок
            del grades[-1]
    return grades # Вернуть массив объектов Grade (оценка) 

def get_all(browser, DB, ix): # Сбор название предмета, оценок и прочего в объект Sub_Gardes (предмет), data - массив объектов пользователя (содержит Sub_Grades, login, password и другое), ix - индекс пользователя в базе данных
    ej_login(browser, DB[ix].login, DB[ix].password) # Вход в аккаунт элжура для дальнейшего функционирования get_subjects и get_grades
    newdata = json.decode(DB[ix].subjects)
    cells = []
    for subject in get_subjects(browser): # Проход по названиям предметов (названия предметов передаются в следующие функции)
        grades = get_grades(subject, browser, DB[ix]) # Массив объектов Grade (оценка)
        mean = do_mean(grades) # Среднее арифметическое оценок
        amean = do_amean(grades) # Среднее арифметическое оценок с учетом а-оценок
        try:
            target = newdata[sbjctix(newdata, subject)].target
            graph = newdata[sbjctix(newdata, subject)].graph
        except:
            target = 0
            graph = []
        cell = Sub_Grades(subject, grades, mean, amean, target, graph) # Занести инофрмацию в объект Sub_Grades (предмет) 
        cells.append(cell) # Занести объект Sub_Grades (предмет) в общий массив
    return cells # Вернуть общий массив


def do_mean(grades): # Среднее арифметическое оценок с учетом коэфицента, grades - массив объектов Grade (оценка)
    summ = 0
    num = 0
    for grade in grades:
        summ += int(grade.grade) * int(grade.coef)
        num += int(grade.coef)
    return int(round(summ/num, 0)) if num != 0 else 0    

def do_amean(grades): # Среднее арифметическое оценок с учетом коэфицента, grades - массив объектов Grade (оценка)
    summ = 0
    num = 0
    for i in range(len(grades)):
        if int(grades[i].agrade) != 0:
            summ += int(grades[i].agrade) * int(grades[i].coef)
            num += int(grades[i].coef)
        else:
            summ += int(grades[i].grade) * int(grades[i].coef)
            num += int(grades[i].coef)
    return int(round(summ/num, 0)) if num != 0 else 0    

def chart(target, num, summ, anum, asumm):
    up = np.vectorize(math.ceil)
    x = np.linspace(target+1, 100, 10)
    x = np.array([el for el, _ in groupby(up(x))])
    y = up((target * num - summ) / (x - target))
    y2 = up((target * anum - asumm) / (x - target))

    xA = np.linspace(10, target-1, 10)
    xA = np.array([el for el, _ in groupby(up(xA))])
    yA = up((target * num - summ) / (xA - target))
    y2A = up((target * anum - asumm) / (xA - target))
    
    xValues = []
    yValues = []
    y2Values = []
    
    for i in range(len(x)):
        xValues.append(int(x[i]))
        if int(y[i]) > 0:
            yValues.append(int(y[i]))
        if int(y2[i]) > 0:
            y2Values.append(int(y2[i]))

    xAValues = []
    yAValues = []
    y2AValues = []

    for j in range(len(xA)):
        xAValues.append(int(xA[j]))
        if int(yA[j]) > 0:
            yAValues.append(int(yA[j]))
        if int(y2A[j]) > 0:
            y2AValues.append(int(y2A[j]))

    graph = [xValues, yValues, y2Values, xAValues, yAValues, y2AValues]

    return graph

def num_summ_counter(grades):
    summ = 0
    num = 0
    asumm = 0
    anum = 0
    for grade in grades:
        summ += int(grade.grade) * int(grade.coef)
        num += int(grade.coef)
    for i in range(len(grades)):
        if int(grades[i].agrade) != 0:
            asumm += int(grades[i].agrade) * int(grades[i].coef)
            anum += int(grades[i].coef)
        else:
            asumm += int(grades[i].grade) * int(grades[i].coef)
            anum += int(grades[i].coef)
    return num, summ, anum, asumm

def id_detect(data, login, password): # Определение поярдкового номера пользователя в базе данных, login / password - введенный пользователем логин / пароль
    for row in data: # Прохождение по каждому пользователю и проверка на идентичность пароля и логина (дл ятого что бы )
        if login == row.login and password == row.password: # Сравнение введенных данных с данными из базы данных (row - каждая строка в табличке бд)
            return int(row.id)
        else:
            continue
    return row.id + 1
def relog_check(data, login, password): # Проверка на наличие введеного логина и пароля в базе данных, login / password - введенный пользователем логин / пароль
    for row in data: # Прохождение по каждому пользователю и проверка на идентичность пароля и логина
        if login == row.login and password == row.password: # Сравнение введенных данных с данными из базы данных (row - каждая строка в табличке бд)
            return False
        else:
            continue
    return True

def ej_login(browser, login, password): # Вход в аккаунт элжур
    browser.get('https://gymn32.eljur.ru/authorize') # Переход на страницу авторизации 
    login_form = browser.find_element(By.XPATH, '//input[@autocomplete = "username"]') # Поиск поля ввода логина
    login_form.click()
    login_form.send_keys(login) # Ввод логина
    password_form = browser.find_element(By.XPATH, '//input[@autocomplete = "current-password"]') # Поиск поля ввода пароля
    password_form.click()
    password_form.send_keys(password) # Ввод пароля
    submit_form = browser.find_element(By.XPATH, '//button[@type="submit"]') # Поиск кнопки отправления информации
    submit_form.click() # После нажатия на кнопку сайт осуществляет переадресацию
    time.sleep(5) # Для полной прогрузки страницы на которую переадресовали необходимо время
    if str(browser.current_url) != 'https://gymn32.eljur.ru/authorize': # Если логин и пароль введен верно, перейти на страницу с успеваемостью
        browser.get("https://gymn32.eljur.ru/journal-student-grades-action")
        return True
    else: # В ином случае вернуть False
        browser.close()
        return False

def get_login(data, request): # Взятие логина пользователя из базы данных
    try:
        return data[int(request.COOKIES['id'])].login # В cookies хранится id (ix) - индекс пользователя в базе данных
    except KeyError:
        return 'СКАУ' # Система контроля академической успеваемости

def sbjctix(newdata, subject_name):
    for i in range(len(newdata)):
                if newdata[i].subject == subject_name:
                    return i
                else:
                    continue
# -------------------- 

# ----------Функции HTML страниц----------
def nuser(request): # Страница регестрации или входа в аккаунт
    data = DataBase.objects.order_by('id') # Массив объектов пользователя (содержит Sub_Grades, login, password и другое)
    context = { # Словарь передаваемый на HTML страницу
        'form': DataBaseForm(), # Объект для отправки форм заполнения
        'login': get_login(data, request) # Отправка логина (необходимо только для вывода логина аккаунт в который вошли в левом верзнем углу)
    }

    rsn = render(request, 'GrdCntrlr/nuser.html', context)
    if request.method == 'POST': # При отправке формы
        browser = webdriver.Safari() # Драйвер на котором работает selenium
        login = request.POST.get('login') # Введенные данные из формы логин
        password = request.POST.get('password') # Введенные данные из формы пароль
        checkbox = request.POST.get('checkbox') # Введенные данные из формы запоминать / незапоминать пользователя
        form = DataBaseForm(request.POST) 
        if ej_login(browser, login, password): # Происходит попытка входа в аккаунт элжура, если вход получлся
            if relog_check(data, login, password): # Проверка на наличие введеного логина и пароля в базе данных
                form.save() # Сохранить введенные данные в бд
            else: 
                print('пара - логин и пароль уже зарегестрирована в бд') # Данные не нужно сохранять повторно так как они уже есть в бд
        else: # Иначе вывести ошибку о неверном логине или пароле
            print('неверный логин или пароль') 
            if relog_check(data, login, password): # Но все равно занести данные в бд (сейчас нужно для тестирования, позже ветвление должно быть исключенно)
                form.save()
            else: 
                print('пара - логин и пароль уже зарегестрирована в бд')

        rsn.delete_cookie('id') # После входа удалить предыдущий coockie с индексом пользователя
        print(id_detect(data, login, password), login, password) 

        if str(checkbox) == 'on': # Если пользователя пожелал запомнить его, установить максимальное время жизни файла coockie
            rsn.set_cookie('id', id_detect(data, login, password), max_age=315336000) # Заносится только индекс пользователя
            print(1)
        else: # Иначе установить время жизни по умолчанию (1 сеанс)
            rsn.set_cookie('id', id_detect(data, login, password))   
            print(0)  
    if len(request.COOKIES) >= 2: # Эта хуйня пока не работает, но по факту если вход прошел успешно то надо переадресовать на другую страницу
        return render(request, 'GrdCntrlr/go_out.html', context)    
    else:
        return rsn

def nuserM(request): # Страница регестрации или входа в аккаунт
    data = DataBase.objects.order_by('id') # Массив объектов пользователя (содержит Sub_Grades, login, password и другое)
    context = { # Словарь передаваемый на HTML страницу
        'form': DataBaseForm(), # Объект для отправки форм заполнения
        'login': get_login(data, request) # Отправка логина (необходимо только для вывода логина аккаунт в который вошли в левом верзнем углу)
    }

    rsn = render(request, 'GrdCntrlr/nuserM.html', context)
    if request.method == 'POST': # При отправке формы
        browser = webdriver.Safari() # Драйвер на котором работает selenium
        login = request.POST.get('login') # Введенные данные из формы логин
        password = request.POST.get('password') # Введенные данные из формы пароль
        checkbox = request.POST.get('checkbox') # Введенные данные из формы запоминать / незапоминать пользователя
        form = DataBaseForm(request.POST) 
        if ej_login(browser, login, password): # Происходит попытка входа в аккаунт элжура, если вход получлся
            if relog_check(data, login, password): # Проверка на наличие введеного логина и пароля в базе данных
                form.save() # Сохранить введенные данные в бд
            else: 
                print('пара - логин и пароль уже зарегестрирована в бд') # Данные не нужно сохранять повторно так как они уже есть в бд
        else: # Иначе вывести ошибку о неверном логине или пароле
            print('неверный логин или пароль') 
            if relog_check(data, login, password): # Но все равно занести данные в бд (сейчас нужно для тестирования, позже ветвление должно быть исключенно)
                form.save()
            else: 
                print('пара - логин и пароль уже зарегестрирована в бд')

        rsn.delete_cookie('id') # После входа удалить предыдущий coockie с индексом пользователя
        print(id_detect(data, login, password), login, password) 

        if str(checkbox) == 'on': # Если пользователя пожелал запомнить его, установить максимальное время жизни файла coockie
            rsn.set_cookie('id', id_detect(data, login, password), max_age=315336000) # Заносится только индекс пользователя
            print(1)
        else: # Иначе установить время жизни по умолчанию (1 сеанс)
            rsn.set_cookie('id', id_detect(data, login, password))   
            print(0)  
    if len(request.COOKIES) >= 2: # Эта хуйня пока не работает, но по факту если вход прошел успешно то надо переадресовать на другую страницу
        return render(request, 'GrdCntrlr/go_outM.html', context)    
    else:
        return rsn

def database(request): # Страница базы данных
    data = DataBase.objects.order_by('id')  
    context = { # Словарь передаваемый на HTML страницу
        'data': data,
        'login': get_login(data, request)
    }
    return render(request, 'GrdCntrlr/database.html', context)

def databaseM(request): # Страница базы данных
    data = DataBase.objects.order_by('id')  
    context = { # Словарь передаваемый на HTML страницу
        'data': data,
        'login': get_login(data, request)
    }
    return render(request, 'GrdCntrlr/databaseM.html', context)

def grades(request):
    graph = []
    ix = int(request.COOKIES['id'])
    data = DataBase.objects.order_by('id')
    if 'refresh' in request.POST: # Обновление списка оценок
        browser = webdriver.Safari()
        newDB = DataBase(ix, data[ix].login, data[ix].password, data[ix].checkbox, json.encode(get_all(browser, data, ix)))
        newDB.save()
    if 'agrade' in request.POST: # Занесения а-оценки в БД
        agrade = request.POST.get('agrade') # А-оценка
        invis_agrade = request.POST.get('invis_agrade') # Индекс оценки: порядковый номер и название предмета (взят из невидимого поля ввода)
        indx = invis_agrade.split('_')[0]
        subject_name = invis_agrade.split('_')[1]
        newdata = json.decode(data[ix].subjects)
        # Проверка а-оценки на допустимость её значения
        try:
            if int(agrade) <= 0 and int(agrade) > 100:
                agrade = 0
                print('превышает допустимое значение')
        except TypeError:
            agrade = 0
            print('неверное значение')
        newdata[sbjctix(newdata, subject_name)].grades[int(indx)].agrade = agrade # Занесения а-оценки в БД
        newdata[sbjctix(newdata, subject_name)].amean = do_amean(newdata[sbjctix(newdata, subject_name)].grades) # Обновление значения amean
        newDB = DataBase(ix, data[ix].login, data[ix].password, data[ix].checkbox, json.encode(newdata))
        newDB.save()
    if 'target' in request.POST:
        target = request.POST.get('target')
        subject_name = request.POST.get('invis_target')
        newdata = json.decode(data[ix].subjects)

        num, summ, anum, asumm = num_summ_counter(newdata[sbjctix(newdata, subject_name)].grades)
        graph = chart(int(target), num, summ, anum, asumm)
        newdata[sbjctix(newdata, subject_name)].target = target     
        newdata[sbjctix(newdata, subject_name)].graph = graph 
        newDB = DataBase(ix, data[ix].login, data[ix].password, data[ix].checkbox, json.encode(newdata))
        newDB.save()

    
    context = {
        'data': json.decode(data[ix].subjects),
        'form': AForm(),
        'login': get_login(data, request),
    }
    return render(request, 'GrdCntrlr/grades.html', context)

def gradesM(request):
    graph = []
    ix = int(request.COOKIES['id'])
    data = DataBase.objects.order_by('id')
    if 'refresh' in request.POST: # Обновление списка оценок
        browser = webdriver.Safari()
        newDB = DataBase(ix, data[ix].login, data[ix].password, data[ix].checkbox, json.encode(get_all(browser, data, ix)))
        newDB.save()
    if 'agrade' in request.POST: # Занесения а-оценки в БД
        agrade = request.POST.get('agrade') # А-оценка
        invis_agrade = request.POST.get('invis_agrade') # Индекс оценки: порядковый номер и название предмета (взят из невидимого поля ввода)
        indx = invis_agrade.split('_')[0]
        subject_name = invis_agrade.split('_')[1]
        print(agrade, indx, subject_name)
        newdata = json.decode(data[ix].subjects)
        # Проверка а-оценки на допустимость её значения
        try:
            if int(agrade) <= 0 and int(agrade) > 100:
                agrade = 0
                print('превышает допустимое значение')
        except TypeError:
            agrade = 0
            print('неверное значение')
        newdata[sbjctix(newdata, subject_name)].grades[int(indx)].agrade = agrade # Занесения а-оценки в БД
        newdata[sbjctix(newdata, subject_name)].amean = do_amean(newdata[sbjctix(newdata, subject_name)].grades) # Обновление значения amean
        newDB = DataBase(ix, data[ix].login, data[ix].password, data[ix].checkbox, json.encode(newdata))
        newDB.save()
    if 'target' in request.POST:
        target = request.POST.get('target')
        subject_name = request.POST.get('invis_target')
        newdata = json.decode(data[ix].subjects)

        num, summ, anum, asumm = num_summ_counter(newdata[sbjctix(newdata, subject_name)].grades)
        graph = chart(int(target), num, summ, anum, asumm)
        newdata[sbjctix(newdata, subject_name)].target = target     
        newdata[sbjctix(newdata, subject_name)].graph = graph 
        newDB = DataBase(ix, data[ix].login, data[ix].password, data[ix].checkbox, json.encode(newdata))
        newDB.save()

    
    context = {
        'data': json.decode(data[ix].subjects),
        'form': AForm(),
        'login': get_login(data, request),
    }
    return render(request, 'GrdCntrlr/gradesM.html', context)
# --------------------