from django.shortcuts import render, redirect, get_object_or_404
from django.views import View, generic
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Post, Connection, Category, Reply,User, UserActiveTokens
from django.db.models import Q
from .forms import PostForm,ReplyForm, RegistrationForm
#from taggit.managers import TaggableManager
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from . import forms
from django.contrib import messages
import datetime
    
##################################################################

"""リスト一覧"""


class Home(LoginRequiredMixin, ListView):
    """HOMEページで、自分以外のユーザー投稿をリスト表示"""
    model = Post
    template_name = 'list.html'

       
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        #get_or_createにしないとサインアップ時オブジェクトがないためエラーになる
        context['connection'] = Connection.objects.get_or_create(user=self.request.user)
        return context
    

class MyPost(LoginRequiredMixin, ListView):
    """自分の投稿のみ表示"""
    model = Post
    template_name = 'list.html'

    def get_queryset(self):
        return Post.objects.filter(user=self.request.user)


class BosyuView(LoginRequiredMixin, ListView):
    """募集のみ表示"""
    model = Post
    template_name = 'list.html'
    def get_queryset(self):
        category = Category.objects.get(name='募集')
        return Post.objects.filter(category=category)

class SitumonView(LoginRequiredMixin, ListView):
    """質問のみ表示"""
    model = Post
    template_name = 'list.html'
    def get_queryset(self):
        category = Category.objects.get(name='質問')
        return Post.objects.filter(category=category)

class ReplyView(LoginRequiredMixin, ListView):
    """返信のみ表示（開発中用、削除予定）"""
    model = Post
    template_name = 'list.html'
    def get_queryset(self):
        category = Category.objects.get(name='返信')
        return Reply.objects.filter(category=category)
    
class Replylist(LoginRequiredMixin, ListView):
    """親投稿に紐づいた返信を表示"""
    model = Post
    template_name = 'reply.html'
    context_object_name = 'replies'  # コンテキストオブジェクト名を追加
 
    
    def get_queryset(self):
        parent_post = Post.objects.get(pk=self.kwargs['pk'])
        category = parent_post.category  # parent_postからcategoryの値を取得
        #category = Category.objects.get(name='返信')
        return Reply.objects.filter(post=parent_post, category=category)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        parent_post = Post.objects.get(pk=self.kwargs['pk'])
        context['parent_post'] = parent_post
        return context




class FollowList(LoginRequiredMixin, ListView):
    """フォローしたユーザーの投稿をリスト表示"""
    model = Post
    template_name = 'list.html'

    def get_queryset(self):
        """フォローリスト内にユーザーが含まれている場合のみクエリセット返す"""
        my_connection = Connection.objects.get_or_create(user=self.request.user)
        all_follow = my_connection[0].following.all()
        return Post.objects.filter(user__in=all_follow)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['connection'] = Connection.objects.get_or_create(user=self.request.user)
        return context

    
class FollowuserList(LoginRequiredMixin, ListView):
    """フォローしたユーザーの名前をリスト表示"""
    model = Post
    template_name = 'followuser-list.html'
    
    def get(self, request):
        user = request.user
        following = user.connection.following.all()
        return render(request, 'followuser-list.html', {'following': following})

#####################################################################


class CreatePost(LoginRequiredMixin, CreateView):
    """投稿フォーム"""
    model = Post
    form_class = PostForm
    template_name = 'create.html'
    success_url = reverse_lazy('mypost')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return kwargs

    def form_valid(self, form):
        """投稿ユーザーをリクエストユーザーと紐付け"""
        form.instance.user = self.request.user
        return super().form_valid(form)


class DetailPost(LoginRequiredMixin, DetailView):
    """投稿詳細ページ"""
    model = Post
    template_name = 'detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['connection'] = Connection.objects.get_or_create(user=self.request.user)
        return context


class UpdatePost(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """投稿編集ページ"""
    model = Post
    form_class = PostForm
    template_name = 'update.html'
    success_url = reverse_lazy('mypost')

    
    
    def test_func(self, **kwargs):
        """アクセスできるユーザーを制限"""
        pk = self.kwargs["pk"]
        post = Post.objects.get(pk=pk)
        return (post.user == self.request.user) 
    




class DeletePost(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """投稿削除ページ"""
    model = Post
    template_name = 'delete.html'
    success_url = reverse_lazy('mypost')

    def test_func(self, **kwargs):
        """アクセスできるユーザーを制限"""
        pk = self.kwargs["pk"]
        post = Post.objects.get(pk=pk)
        return (post.user == self.request.user) 

###############################################################
"""返信機能"""

class ReplyCreate(LoginRequiredMixin, CreateView):
    """返信を作成"""
    model = Reply
    form_class = ReplyForm
    template_name = 'replycreate.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return kwargs

    def form_valid(self, form):
        parent_post = Post.objects.get(pk=self.kwargs['pk'])  # 親投稿を取得
        form.instance.parent_post = parent_post  # 返信オブジェクトに親投稿を紐付ける
        form.instance.user = self.request.user  # 返信したユーザーを設定
        form.instance.category = Category.objects.get(name='返信')
        form.instance.post = parent_post  # 返信のpostフィールドに親投稿を設定
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('detail', kwargs={'pk': self.kwargs['pk']})
        

    
class ReplyUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """返信編集ページ"""
    model = Reply
    form_class = ReplyForm
    template_name = 'replyupdate.html'
    success_url = reverse_lazy('mypost')

    
    
    def test_func(self, **kwargs):
        """アクセスできるユーザーを制限"""
        pk = self.kwargs["pk"]
        post = Reply.objects.get(pk=pk)
        return (post.user == self.request.user)



class ReplyDetail(LoginRequiredMixin, DetailView):
    """返信詳細ページ"""
    model = Reply
    template_name = 'replydetail.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['connection'] = Connection.objects.get_or_create(user=self.request.user)
        return context   



###############################################################
#いいね処理
class LikeBase(LoginRequiredMixin, View):
    """いいねのベース。リダイレクト先を以降で継承先で設定"""
    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        related_post = Post.objects.get(pk=pk)

        if self.request.user in related_post.like.all():
            obj = related_post.like.remove(self.request.user)
        else:
            obj = related_post.like.add(self.request.user)  
        return obj

class LikeList(LoginRequiredMixin,ListView):
    
    model = Post
    template_name = 'related_post.html'
    
    def get(self, request):
        user = request.user
        related_post = user.related_post.all()
        return render(request, 'related_post.html', {'related_post': related_post})

class LikeHome(LikeBase):
    """HOMEページでいいねした場合"""
    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        return redirect('home')

class LikeLikelist(LikeBase):
    """いいね一覧ページでいいねした場合"""
    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        return redirect('related_post')

class LikeDetail(LikeBase):
    """詳細ページでいいねした場合"""
    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        pk = self.kwargs['pk'] 
        return redirect('detail', pk)
    
class LikeUser(LikeBase):
    """ユーザページでいいねした場合"""
    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        pk = self.kwargs['pk'] 
        return redirect('look_user', pk)
###############################################################


#フォロー処理

class FollowBase(LoginRequiredMixin, View):
    """フォローのベース。リダイレクト先を以降で継承先で設定"""
    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        target_user = Post.objects.get(pk=pk).user

        my_connection = Connection.objects.get_or_create(user=self.request.user)

        if target_user in my_connection[0].following.all():
            obj = my_connection[0].following.remove(target_user)
        else:
            obj = my_connection[0].following.add(target_user)
        return obj

class FollowHome(FollowBase):
    """HOMEページでフォローした場合"""
    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        return redirect('home')

class FollowDetail(FollowBase):
    """詳細ページでフォローした場合"""
    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        pk = self.kwargs['pk'] 
        return redirect('detail', pk)
    
class FollowUser(FollowBase):
    """ユーザページでフォローした場合"""
    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        pk = self.kwargs['pk'] 
        return redirect('look_user', pk)
###############################################################


#Tag検索機能

class TagView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'list.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        q_word = self.request.GET.get('query')

        if q_word:
            return Post.objects.filter(tags__name__icontains=q_word)
        else:
            return Post.objects.all()
        
    def get_queryset(self):
        q_word = self.request.GET.get('query')
        
        if q_word:
            keywords = q_word.split()  # キーワードを分割してリストとして保持
            
            # 各キーワードを含む投稿をフィルタリング
            queryset = Post.objects.filter(
                Q(tags__name__icontains=keywords[0])  # 最初のキーワード
            )
            
            for keyword in keywords[1:]:
                queryset = queryset.filter(
                    Q(tags__name__icontains=keyword)  # 残りのキーワードはAND検索として追加フィルタリング
                )
            
            return queryset
        else:
            return Post.objects.all()

        

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        q_word = self.request.GET.get('query')
        context['tag'] = q_word  # 検索キーワードをテンプレートに渡す
        return context

#############################################################################

class FollowList(LoginRequiredMixin, ListView):
    """フォローしたユーザーの投稿をリスト表示"""
    model = Post
    template_name = 'list.html'

    def get_queryset(self):
        """フォローリスト内にユーザーが含まれている場合のみクエリセット返す"""
        my_connection = Connection.objects.get_or_create(user=self.request.user)
        all_follow = my_connection[0].following.all()
        return Post.objects.filter(user__in=all_follow)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['connection'] = Connection.objects.get_or_create(user=self.request.user)
        return context



class LookUser(View):#要確認
    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        user = post.user
        #誕生日からage算出
        if user.date_of_birth:
            today = datetime.date.today()
            birthday = user.date_of_birth
            age = (int(today.strftime("%Y%m%d")) - int(birthday.strftime("%Y%m%d"))) // 10000
        else:
            age = "未設定"
        items = Post.objects.filter(user_id=user.id)
        connection = Connection.objects.get_or_create(user=self.request.user)
        
        return render(request, 'look_user.html', {'user': user, 'age': age, 'items': items, 'connection': connection})


#プロフィール編集
@login_required
def edit_user(request):
  edit_form = forms.UserEditForm(
    request.POST or None, 
    request.FILES or None, 
    instance = request.user
    )
  if edit_form.is_valid():
    messages.success(request, '＝プロフィールが更新されました＝')
    edit_form.save()
    #print(edit_form.cleaned_data)
  return render(request, 'user_edit_page.html', context={
      'edit_form': edit_form,
  })

#ユーザ登録
def signup(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            # 登録が成功した場合のリダイレクトなどの処理を記述
    else:
        form = RegistrationForm()
    return render(request, 'signup.html', {'form': form})

def active_user(request, token):
    user_active_token = UserActiveTokens.objects.active_user_using_token(token)
    return render(
      request, 'active_user.html'
    )

#LikeUser.as_view(), name='like-user'),

#class EditUserView(View):
#    @login_required
#    def get(self, request):
#        edit_form = UserEditForm(instance=request.user)
#        return render(request, 'user_edit_page.html', {'edit_form': edit_form})
#    
#    @login_required
#    def post(self, request):
#        edit_form = UserEditForm(request.POST, request.FILES, instance=request.user)
#        if edit_form.is_valid():
#            edit_form.save()
#            messages.success(request, 'プロフィールが更新されました')
#            return redirect('profile')  # リダイレクト先のURLを指定してください
#        return render(request, 'user_edit_page.html', {'edit_form': edit_form})


#class SignupView(View):
#    def get(self, request):
#        form = RegistrationForm()
#        return render(request, 'signup.html', {'form': form})
#
#    def post(self, request):
#        form = RegistrationForm(request.POST)
#        if form.is_valid():
#            form.save()
#            # 登録が成功した場合のリダイレクトなどの処理を記述
#            return redirect('login')  # リダイレクト先のURLを指定してください
#        return render(request, 'signup.html', {'form': form})


#class ActiveUserView(View):
#    def get(self, request, token):
#        user_active_token = UserActiveTokens.objects.active_user_using_token(token)
#        return render(request, 'active_user.html')