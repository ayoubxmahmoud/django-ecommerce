from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Customer


class CustomerCreationForm(UserCreationForm):
    class Meta:
        model = Customer
        fields = ['name', 'email','username', 'password1', 'password2']



class CustomerUpdateForm(ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'username', 'email', 'avatar']
