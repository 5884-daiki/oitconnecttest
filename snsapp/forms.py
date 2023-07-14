#from unicodedata import category
from django import forms
from .models import Post , Reply, User
from django.forms.widgets import ClearableFileInput#, CheckboxInput, HiddenInput
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password



class SingleFileInput(ClearableFileInput):
    def value_from_datadict(self, data, files, name):
        upload = super().value_from_datadict(data, files, name)
        if isinstance(upload, list):
            return upload[0]
        return upload

class SingleFileField(forms.FileField):
    widget = SingleFileInput

class PostForm(forms.ModelForm):
    image = SingleFileField(required=False, widget=SingleFileInput)
    
    class Meta:
        model = Post
        fields = ['title', 'content', 'image','category','tags']


class ReplyForm(forms.ModelForm):
    image = SingleFileField(required=False, widget=SingleFileInput)
    
    class Meta:
        model = Reply
        fields = ['content', 'image']


class UserEditForm(forms.ModelForm):
  COURCES = (
      ('R',"R科"),
      ('S',"S科"),
      ('W',"W科"),
  )
  username = forms.CharField(label='名前を入力してください')
  date_of_birth = forms.DateField(label='birth day')
  email = forms.EmailField(label='email')
  course = forms.fields.ChoiceField(label="学科を入力してください", choices=COURCES, required=True, widget=forms.widgets.Select)
  sns = forms.MultipleChoiceField(
    label = "SNS",
    required=False,
    disabled=False,
    initial=[],
    choices=[('ins',"Instagram"),('twi',"Twitter"),('oth',"その他")],
    widget=forms.CheckboxSelectMultiple
  )
  url_ins = forms.URLField(label='InstagramのURLを入力してください', max_length=200, required=False)
  url_twi = forms.URLField(label='TwitterのURLを入力してください', max_length=200, required=False)
  url_oth = forms.URLField(label='Instagram,Twitter以外のURLを入力してください', max_length=200, required=False)
  circle = forms.CharField(label='所属サークルを入力してください', max_length=200, required=False)
  hobby = forms.CharField(label='趣味', max_length=200)
  #tag
  introduce = forms.CharField(label='自己紹介', max_length=500)
  picture = forms.FileField(label='picture', required=False)

  class Meta:
    model = User
    fields = ('username', 'date_of_birth', 'email', 'course', 'sns', 'url_ins', 'url_twi', 'url_oth', 'circle', 'hobby', 'introduce')

'''
class ChangePasswordForm(forms.ModelForm):
    
  password = forms.CharField(label='password', widget=forms.PasswordInput())
  reenter_password = forms.CharField(label='re-enter password', widget=forms.PasswordInput())

  class Meta():
    model = User
    fields = ('password',)
'''
class RegistrationForm(forms.ModelForm):
  COURCES = (
      ('r',"R科"),
      ('s',"S科"),
      ('w',"W科"),
  )
  username = forms.CharField(label='user name')
  date_of_birth = forms.DateField(label='birth day')
  email = forms.EmailField(label='email')
  course = forms.fields.ChoiceField(label="学科", choices=COURCES, required=True, widget=forms.widgets.Select)
  circle = forms.CharField(label='所属サークルを入力してください', max_length=200)
  hobby = forms.CharField(label='趣味', max_length=200)
  #tag
  introduce = forms.CharField(label='自己紹介', max_length=500)
  password = forms.CharField(label='password', widget=forms.PasswordInput())
  reenter_password = forms.CharField(label='re-enter password', widget=forms.PasswordInput())

  class Meta():
    model = User
    fields = ('username', 'date_of_birth', 'email', 'course', 'circle', 'hobby', 'introduce', 'password')

  def clean(self):
    cleaned_data = super().clean()
    password = cleaned_data['password']
    reenter_password = cleaned_data['reenter_password']
    if password != reenter_password:
      raise forms.ValidationError('Password is different. Please try again')

  def save(self, commit=False):
    r_user = super().save(commit=False)
    validate_password(self.cleaned_data['password'], r_user)
    r_user.set_password(self.cleaned_data['password'])
    r_user.save()
    return r_user