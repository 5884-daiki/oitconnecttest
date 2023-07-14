from django.db import models
from django.contrib.auth.models import User
from taggit.managers import TaggableManager

from django.contrib.auth.models import AbstractBaseUser, Group, PermissionsMixin
from taggit.managers import TaggableManager
from django.contrib.auth.models import UserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from uuid import uuid4
from datetime import datetime, timedelta, timezone
#メール
import smtplib
from email.mime.multipart import  MIMEMultipart
from email.mime.text import MIMEText
# Create your models here.


class User(AbstractBaseUser, PermissionsMixin):
    COURCES = (
      ('R',"R科"),
      ('S',"S科"),
      ('W',"W科"),
    )
    username = models.CharField(max_length=100, unique=False)
    email = models.EmailField(max_length=100, unique=True)
    course = models.CharField(max_length=10, choices=COURCES, blank=True)
    sns = models.CharField(max_length=255, blank=True)
    url_ins = models.URLField(max_length=200, blank=True)
    url_twi = models.URLField(max_length=200, blank=True)
    url_oth = models.URLField(max_length=200,)
    circle = models.CharField(max_length=100, blank=True)
    hobby = models.CharField(max_length=100, default="未設定")
    #tag
    introduce = models.CharField(max_length=500, default="未設定")#要確認(誕生日不要？formでbirthdayからage計算?)
    date_of_birth = models.DateField(null='2000-1-1')
    is_active = models.BooleanField(default=False)##あとで変更、要確認
    is_staff = models.BooleanField(default=False)
    picture = models.FileField(null=True, upload_to='picture/')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'user'


class Category(models.Model):
    name = models.CharField('カテゴリー', max_length=50,unique=True )

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    like = models.ManyToManyField(User, related_name='related_post', blank=True)
    created_at = models.DateTimeField('作成日', auto_now_add=True)
    #updated_at = models.DateField('更新日', auto_now=True)
    category = models.ForeignKey(Category, verbose_name='カテゴリー', on_delete=models.PROTECT, default='返信')
    tags = TaggableManager(blank=True)
    reply = models.TextField()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_at"]
        verbose_name = '投稿'
        verbose_name_plural = '投稿'


class Connection(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    following = models.ManyToManyField(User, related_name='followers', blank=True)

    def __str__(self):
        return self.user.username


class Reply(models.Model):
    content = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='replies')
    category = models.ForeignKey(Category, verbose_name='カテゴリー', on_delete=models.PROTECT, default='返信')
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    created_at = models.DateField('作成日', auto_now_add=True)
 
    #tags = TaggableManager(blank=True)

    def __str__(self):
        return self.content

    class Meta:
        ordering = ["-id"]
        verbose_name = '返信'
        verbose_name_plural = '返信'


class UserActiveTokensManager(models.Manager):

  def active_user_using_token(self, token):
    user_active_token = self.filter(
      token=token,
      expired_time__gte=datetime.now()
    ).first()
    r_user = user_active_token.r_user
    r_user.is_active = True
    r_user.save()

class UserActiveTokens(models.Model):
  token = models.UUIDField(db_index=True)
  expired_time = models.DateTimeField()
  r_user = models.ForeignKey(
    'User', on_delete=models.CASCADE
  )

  objects = UserActiveTokensManager()

  class Meta:
    db_table = 'user_active_tokens'

@receiver(post_save, sender=User)
def publish_token(sender, instance, **kwargs):
  print(datetime.now() + timedelta(hours=5))
  user_active_token = UserActiveTokens.objects.create(
    r_user=instance, 
    token=str(uuid4()),
    expired_time=datetime.now() + timedelta(hours=5)
  )

  url = f'http://127.0.0.1:8000/email_authentication/active_user/{user_active_token.token}'
  
  if instance.is_active == 0:
    # メールでURLを送る
    smtp_server = "smtp.gmail.com"
    port = 587
    server = smtplib.SMTP(smtp_server, port)
    server.starttls()
    login_address = "monodezacomm1@gmail.com"
    login_password = "ufqalgdqiazlcmde" #OIT_monodeza_C1
    server.login(login_address, login_password)
    message = MIMEMultipart()
    message["Subject"] = "OIT-Connect　アカウント登録フォーム" #件名
    message["From"] = "monodezacomm1@gmail.com" #メールの送信元
    message["To"] = str(instance) #メールの送信先（本番）
    #message["To"] = "e1921062@oit.ac.jp" #メールの送信先（テスト）
    text = MIMEText(
      #本文を入力
      str(instance)+"様\n"
      "この度はOIT-Connectにご登録いただき誠にありがとうございます。\n"
      "以下のURLへのアクセスを以って新規会員登録が完了いたします。\n"
      "仮登録のデータは本日23時59分に削除されますので、お早めに下記URLよりご登録下さい。\n"
      + str(url)
    ) 
    message.attach(text)
    server.send_message(message)
    server.quit() #サーバー切断
    print("メールを送信しました。")

#ログ
  print(str(url))
  print("シグナル(publish_token)が実行されました。")