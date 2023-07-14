from django.urls import path
from snsapp.views import TagView
from . import views
from .views import Home, MyPost, CreatePost, DetailPost, UpdatePost, DeletePost,\
                   LikeHome, FollowHome, FollowDetail, FollowList, LikeDetail, \
                    BosyuView, SitumonView,LikeLikelist, FollowuserList, \
                        LikeList, Replylist, ReplyCreate, ReplyView, ReplyUpdate, ReplyDetail, \
                     LookUser,  LikeUser, FollowUser, \
                         edit_user,active_user


urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('mypost/', MyPost.as_view(), name='mypost'),
    path('create/', CreatePost.as_view(), name='create'),
    path('detail/<int:pk>/', DetailPost.as_view(), name='detail'),
    path('detail/<int:pk>/update/', UpdatePost.as_view(), name='update'),
    path('detail/<int:pk>/delete/', DeletePost.as_view(), name='delete'),
    path('look_user/<int:pk>/', LookUser.as_view(), name='look_user'),#要確認
    path('like-home/<int:pk>/', LikeHome.as_view(), name='like-home'),
    path('like-detail/<int:pk>/', LikeDetail.as_view(), name='like-detail'),
    path('like-likelist/<int:pk>/', LikeLikelist.as_view(), name='like-likelist'),
    path('like-user/<int:pk>', LikeUser.as_view(), name='like-user'),
    path('follow-home/<int:pk>/', FollowHome.as_view(), name='follow-home'),
    path('follow-detail/<int:pk>/', FollowDetail.as_view(), name='follow-detail'),
    path('follow-list/', FollowList.as_view(), name='follow-list'),
    path('bosyu/', BosyuView.as_view(), name='bosyu'),
    path('situmon/', SitumonView.as_view(), name='situmon'),
    path('tag/', TagView.as_view(), name='tag-search'),
    path('followuser-list/', FollowuserList.as_view(), name='followuser_list'),
    path('like-list/', LikeList.as_view(), name='related_post'),
    path('replycreate/<int:pk>/', ReplyCreate.as_view(), name='replycreate'),
    path('reply-list/<int:pk>/', Replylist.as_view(), name='reply-list'),
    path('reply/', ReplyView.as_view(), name='reply'),
    path('replyupdate/<int:pk>/', ReplyUpdate.as_view(), name='replyupdate'),
    path('replydetail/<int:pk>/', ReplyDetail.as_view(), name='replydetail'),
    path('edit_user' ,views.edit_user, name='edit_user'),#要確認
    path('accounts/signup/', views.signup, name='signup'),
    path('email_authentication/active_user/<uuid:token>', views.active_user, name='active_user'),
]

    

    #path('edit/', EditUserView.as_view(), name='edit_user'),#要確認
    #path('signup/', SignupView.as_view(), name='signup'),
    #path('activate/<str:token>/', ActiveUserView.as_view(), name='activate_user'),

