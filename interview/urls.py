from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('permission/', views.permission, name='permission'),
    path('resume/', views.resume_upload, name='resume_upload'),
    path('mode/', views.mode_select, name='mode_select'),
    path('interview/', views.interview, name='interview'),
    path('api/submit_answer/', views.submit_answer, name='submit_answer'),
    path('api/next_question/', views.next_question, name='next_question'),
    path('result/', views.result, name='result'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('myinterviews/', views.myinterviews, name='myinterviews'),
    path('profile/', views.profile, name='profile'),
]