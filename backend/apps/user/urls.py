from user import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

utils_router = DefaultRouter()

utils_router.register('profile', views.UserProfileViewSet)

utils = [
    path('username/otp/', views.OtpUsernameView.as_view()),
    path('update/email/', views.UserEmailChangeView.as_view()),
    path('update/', views.UserUpdateView.as_view()),
    path('email/verify/', views.UserEmailVerifyView.as_view())
] + utils_router.urls


password_urls = [
    path('reset/send/', views.PasswordResetSendView.as_view()),
    path('reset/change/', views.PasswordResetConfirmView.as_view()),
    path('change/', views.PasswordChangeView.as_view()),
]

auth_urls = [
    path('activate/', views.ActivateUserView.as_view()),
    path('is/logged/', views.is_logged_in),
    path('token/refresh/', TokenRefreshView.as_view()),
    path('signup/', views.SignupView.as_view()),
    path('login/', views.JWTLoginView.as_view()),
    path('password/', include(password_urls))
]

urlpatterns = [
    path('auth/', include(auth_urls)),
    path('utils/', include(utils)),
]

