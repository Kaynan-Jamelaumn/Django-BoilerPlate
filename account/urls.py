from django.urls import path
from . import views 

app_name = 'account'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('update/', views.update_user, name='update'),
    path('filter-users/', views.filter_users, name='filter_users'),
]
