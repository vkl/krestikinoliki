"""krestikinoliki URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from krestikinoliki import views 

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^index/', views.index, name='index'),
    url(r'^logout/', views.do_logout, name='do_logout'),
    url(r'^registration/', views.do_registry, name='do_registry'),
    url(r'^active_users/', views.active_users, name='active_users'),
    url(r'^inviteuser/', views.invite_user, name='invite_user'),
    url(r'^status_game/(?P<game_id>.*)', views.status_game, name='status_game'),
    url(r'^status_user/', views.status_user, name='status_user'),
    url(r'^set_game/', views.set_game, name='set_game'),
    url(r'^.*', views.default),
]
