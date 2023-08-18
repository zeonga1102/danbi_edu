from django.urls import path
from user import views


urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("login", views.LogInView.as_view(), name="login"),
    path("signup", views.SignUpView.as_view(), name="signup"),
]