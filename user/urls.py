from django.urls import path
from . import views

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('refresh-token/', TokenRefreshView.as_view(), name='refresh-token'),
    # path('login-old/', views.LoginView.as_view()),
    path('signup/', views.SignupView.as_view()),
    path('get-user/', views.GetUserView.as_view()),
    path('update-user/', views.UpdateUserView.as_view()),
    path('deactivate-account/', views.DeactivateUserView.as_view()),
    path('activate-account/', views.ActivateUserView.as_view()),

    # path('update-profile-picture', views.UpdateProfilePictureView.as_view()),

    path('verify-email/', views.EmailVerificationView.as_view()),
    path('send-email-verification-code/', views.SendEmailVerificationCodeView.as_view(),
         name='send-email-verification-code'),
    path('forgot-password/', views.ForgotPasswordView.as_view()),
    path('reset-password/', views.ResetPasswordView.as_view()),
    path('change-password/', views.ChangePasswordView.as_view()),
]
