'''
Created on 2 september 2015

@author: vkl
'''

from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(max_length=24)
    password = forms.PasswordInput()
