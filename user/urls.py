from django.urls import path
from . import views

urlpatterns = [
    path('login', views.LoginView.as_view()),
    path('signup', views.SignupView.as_view()),
    path('get-user', views.UserView.as_view()),
    path('update-user', views.UpdateUserView.as_view()),

    path('verify-email', views.EmailVerificationView.as_view()),
    path('send-email-verification-code/', views.SendEmailVerificationCodeView.as_view(),
         name='send-email-verification-code'),
    path('forgot-password', views.ForgotPasswordView.as_view()),
    path('reset-password', views.ResetPasswordView.as_view()),
    path('change-password', views.ChangePasswordView.as_view()),
]
