from django.urls import path

from . import views
urlpatterns = [
    path('create-user/',views.CreateUseer.as_view(),name='AccountCreation'),
    path('forget-password/',views.RequestPasswordReset.as_view(),name='RequestPasswordReset'),
    path('verify-otp/',views.VerifyOTP.as_view(),name='VerifyOTP'),
    path('reset-password/',views.ResetPassword.as_view(),name='ResetPassword'),
    path('logout/',views.logout,name='logout'),
]
