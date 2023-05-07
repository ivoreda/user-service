from django.urls import path
from . import views

urlpatterns = [
    path('login', views.LoginView.as_view()),
    path('signup', views.SignupView.as_view()),
    path('get-user', views.UserView.as_view()),
    path('update-user', views.UpdateUserView.as_view()),
]