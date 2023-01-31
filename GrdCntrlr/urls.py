from django.urls import path
from . import views

urlpatterns = [
    path('nuser', views.nuser, name='nuser'),
    path('go_out', views.nuser, name='go_out'),
    path('database', views.database, name='database'),
    path('grades', views.grades, name='grades'),
    path('nuser_mobile', views.nuserM, name='nuser_mobile'),
    path('go_out_mobile', views.nuserM, name='go_out_mobile'),
    path('db_adm', views.databaseM, name='db_adm'),
    path('grades_mobile', views.gradesM, name='grades_mobile'),
    path('about_mobile', views.aboutM, name='about_mobile'),
    path('favorite_grades', views.favM, name='favorite_grades'),
]