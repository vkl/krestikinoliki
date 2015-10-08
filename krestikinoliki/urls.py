from django.conf.urls import patterns, include, url
from krestikinoliki import views
from krestikinoliki.views import Index, Default, Logout, Registration, Registered, StatusGame, SetGame, InviteUser, ActiveUsers, StatusUser, Tetris

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'krestikinoliki.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^index', Index.as_view()),
    url(r'^logout/', Logout.as_view()),
    url(r'^registration/', Registration.as_view()),
    url(r'^registered/', Registered.as_view()),
    url(r'^active_users/', ActiveUsers.as_view()),
    url(r'^inviteuser/', InviteUser.as_view()),
    url(r'^status_game/(?P<game_id>.*)', StatusGame.as_view()),
    url(r'^status_user/', StatusUser.as_view()),
    url(r'^set_game/', SetGame.as_view()),
    url(r'^tetris', Tetris.as_view()),
    url(r'^.*', Default.as_view()),
)
