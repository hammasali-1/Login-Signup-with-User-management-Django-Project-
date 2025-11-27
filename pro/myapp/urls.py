"""
URL configuration for pro project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("",views.index,name='index'), 
    path("myfile/",views.myfile,name='myfile'),
    path("profile/",views.profile,name='profile'),
    path('login/',views.login,name='login'),
    path('signup/',views.signup,name='signup'),
    path('logout/',views.mylogout,name='logout'),
    path('del/<int:id>',views.delete,name='del'),
    path('update/<int:id>',views.update,name='update'),
    path('create_user/',views.create_user,name='create_user'),
    path('bulk_action/',views.bulk_action,name='bulk_action'),
    path('toggle_status/',views.toggle_status,name='toggle_status')
    ,path('upload_profile_image/',views.upload_profile_image,name='upload_profile_image')
    ,path('delete_profile_image/',views.delete_profile_image,name='delete_profile_image')
    ,path('change_password/',views.change_password,name='change_password')
    ,path('stats/',views.stats,name='stats')
    ,path('delete_account/',views.delete_account,name='delete_account')
    ,path('contact/',views.contact,name='contact')
    ,path('about/',views.about,name='about')
    ,path('edit_contact/',views.edit_contact,name='edit_contact')
    ,path('edit_about/',views.edit_about,name='edit_about')
    ,path('inbox/',views.inbox,name='inbox')
    ,path('inbox/user/<int:user_id>/',views.inbox_user,name='inbox_user')
    ,path('inbox/bulk_action/',views.inbox_bulk_action,name='inbox_bulk_action')
    ,path('inbox/delete/<int:id>/',views.inbox_delete_message,name='inbox_delete_message')
    ,path('inbox/delete_user/<int:user_id>/',views.inbox_delete_user,name='inbox_delete_user')
    ,path('set_theme/',views.set_theme,name='set_theme')
    ,path('inbox/data/',views.inbox_data,name='inbox_data')

]
