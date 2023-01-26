from django.urls import path
from . import views

urlpatterns = [
    path('nuser', views.nuser, name='nuser'),
    path('go_out', views.nuser, name='go_out'),
    path('database', views.database, name='database'),
    path('grades', views.grades, name='grades'),
    path('nuserM', views.nuserM, name='nuserM'),
    path('go_outM', views.nuserM, name='go_outM'),
    path('databaseM', views.databaseM, name='databaseM'),
    path('gradesM', views.gradesM, name='gradesM'),
]