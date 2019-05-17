from django import forms
'''
class RegisterForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(max_length=50)
    email = forms.CharField(max_length=100)

class LoginForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(max_length=50)
'''
class DirectionForm(forms.Form):
    direction = forms.CharField(max_length=10)
    size = forms.IntegerField()

class SubmitScoreForm(forms.Form):
    size = forms.IntegerField()
    score = forms.IntegerField()
    
