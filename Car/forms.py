__author__ = 'KATE'
from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from .models import Comments


class CommentForm(ModelForm):
    class Meta:
        model = Comments
        fields = ['ctext']


class Registration(ModelForm):
    class Meta:
        model = User

class CarAddToCartForm(forms.Form):
    quantity = forms.IntegerField(widget=forms.TextInput(attrs={'size':'2', 'value':'1', 'class':'quantity', 'maxlength':'5'}),
               error_messages={'invalid':'Please enter a valid quantity.'}, min_value=1)
    car_slug = forms.CharField(widget=forms.HiddenInput())

def _init_(self, request=None, *args, **kwargs):
    self.request = request
    super(CarAddToCartForm, self)._init_(*args, **kwargs)

def clean(self):
    if self.request:
        if not self.request.session.test_cookie_worked():
            raise forms.ValidationError("Cookies must be enabled.")
        return self.cleaned_data
