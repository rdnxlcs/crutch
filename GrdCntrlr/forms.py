from .models import DataBase, A
from django.forms import CheckboxInput, ModelForm, TextInput

class DataBaseForm(ModelForm):
    class Meta:
        model = DataBase
        fields = ['login', 'password', 'checkbox']
        widgets = {
            'login': TextInput(attrs={
                'class': 'form-control',
                'type': 'text',
                'name': 'login',
            }),
            'password': TextInput(attrs={
                'class': 'form-control',
                'type': 'text',
                'id': 'inputPassword',
                'name': 'password',
            }),
            'checkbox': CheckboxInput(attrs={
                'class': 'form-check-input',
                'type': 'checkbox',
                'checked': '',
                'name': 'checkbox',
            }),
        }

class AForm(ModelForm):
    class Meta:
        model = A
        fields = ['agrade', 'invis_indx']
        widgets = {
            'agrade': TextInput(attrs={
                'class': 'form-control table-input',
                'placeholder': '0',
                'size': '1',
                'type': 'text',
                'name': 'agrade',
            }),
            'invis_indx': TextInput(attrs={
                'class': 'form-control table-input invis_indx',
                'hidden': 'false',
                'type': 'text',
                'name': 'invis_indx',
            }),
        }
