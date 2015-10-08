'''
Created on 2 september 2015
@author: vkl
'''

from django.shortcuts import render, redirect
from django.shortcuts import HttpResponse, Http404
#from django.http import JsonResponse
#from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.views.generic import View
from django.views.defaults import page_not_found

from datetime import datetime

#from krestikinoliki.models import Sensor, Location
#from krestikinoliki.forms import LoginForm
from krestikinoliki.settings import BASE_DIR, APP_NAME

import logging
import os
import json

#from pip._vendor import requests
#from pip._vendor.requests.packages.urllib3.util import request
#from test.test_urllib2 import RequestTests
#from _sqlite3 import IntegrityError
from krestikinoliki.models import Game, UserProfile
#from pip._vendor import requests

LOG_FILE = os.path.join(BASE_DIR, "{:s}.log".format(APP_NAME))

logger = logging.Logger("krestikinoliki")
logger.setLevel(logging.ERROR)
#fileHd = logging.FileHandler(LOG_FILE)
streamHd = logging.StreamHandler()
#logger.addHandler(fileHd)
logger.addHandler(streamHd)

# Create your views here.


class HttpResponseUnauthorized(HttpResponse):
    status_code = 401


def get_template_by_lang(request):

    cookie_lang = None
    template = "eng_index.html"

    if "lang" in request.GET:
        if request.GET["lang"] == 'rus':
            template = "rus_index.html"
            cookie_lang = 'rus'
        elif request.GET["lang"] == 'eng':
            template = "eng_index.html"
            cookie_lang = 'eng'

    elif "lang" in request.COOKIES:
        if request.COOKIES["lang"] == "eng":
            template = "eng_index.html"
        elif request.COOKIES["lang"] == "rus":
            template = "rus_index.html"
        cookie_lang = request.COOKIES["lang"]

    return (template, cookie_lang)


class Tetris(View):

    def get(self, request):
        return render(request, "tetris.html")


class Logout(View):

    def get(self, request):
        # user logout
        # remove all games for user
        try:
            u = User.objects.get(username=request.user)
            games = Game.objects.filter(player_first=u.id).exclude(status=4)
            list(map(lambda x: x.delete(), games))
            games = Game.objects.filter(player_second=u.id).exclude(status=4)
            list(map(lambda x: x.delete(), games))
            logout(request)
        except User.DoesNotExist:
            pass
        finally:
            return redirect("/index/")

class Registration(View):

    def get(self, request):
        (template, cookie_lang) = get_template_by_lang(request)
        response = render(request, template, {"registration_required": True})
        if cookie_lang:
            response.set_cookie("lang", cookie_lang)
        return response

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        try:
            logger.debug("Try to create user")
            user = User.objects.create_user(username=username, password=password)
            user_profile = UserProfile.objects.create(user=user)
            user.save()
            user_profile.save()
            logger.debug("Registry success")
            response = redirect("/registered/")
        except Exception as e:
            logger.error("Could not create user. Error {:}".format(e))
            (template, cookie_lang) = get_template_by_lang(request)
            response = render(request, template, {"registration_required": True, "user_error": username})
            if cookie_lang:
                response.set_cookie("lang", cookie_lang)
        return response


class Registered(View):

    def get(self, request):
        if request.user.is_authenticated():
            response = page_not_found(request)
        else:
            template_data = {}
            template_data["login_required"] = True
            template_data["registration_success"] = True
            (template, cookie_lang) = get_template_by_lang(request)
            response = render(request, template, template_data)
            if cookie_lang:
                response.set_cookie("lang", cookie_lang)
        return response


def game_logic(message):
    """Game logic
    """
    move_length = 4
    x = -1
    y = -1
    g = [['', '', ''], ['', '', ''], ['', '', '']]
    for pos in range(0, len(message), move_length):
        if (message[pos+1:pos+2].isdigit() and (message[pos+3:pos+4].isdigit())):
            y = int(message[pos+1:pos+2])
            x = int(message[pos+3:pos+4])
            g[y][x] = message[pos:pos+1]
    def check(line):
        if 'x' == line[0] == line[1] == line[2]:
            return 1
        elif 'o' == line[0] == line[1] == line[2]:
            return 2
        elif (('' == line[0]) or ('' == line[1]) or ('' == line[2])):
            return -1
        else:
            return 0
    # horizontal
    r = list(map(check, g))
    # vertical
    r.extend(list(map(check, [[g[0][0], g[1][0], g[2][0]], [g[0][1], g[1][1], g[2][1]], [g[0][2], g[1][2], g[2][2]]])))
    # diagonal
    r.extend(list(map(check, [[g[0][0], g[1][1], g[2][2]], [g[2][0], g[1][1], g[0][2]]])))
    res = list(filter(lambda x: x == 1, r))
    if len(res) > 0:
        return 1
    res = list(filter(lambda x: x == 2, r))
    if len(res) > 0:
        return 2
    res = list(filter(lambda x: x == -1, r))
    if len(res) > 0:
        return -1
    return 0

class StatusUser(View):

    def head(self, request):
        if not request.user.is_authenticated():
            return HttpResponseUnauthorized()
        # update session expiration
        request.session.set_expiry(10)

        return HttpResponse("")

    def get(self, request):
        if not request.user.is_authenticated():
            return HttpResponseUnauthorized()

        try:

            current_user = User.objects.get(username=request.user)

            def user_is_logged(user_id):
                retval = False
                sessions = list(filter(lambda s: "_auth_user_id" in s.get_decoded(), Session.objects.filter(expire_date__gte=datetime.now())))
                if len( list(filter(lambda s: int(user_id) == int(s.get_decoded()['_auth_user_id']), sessions)) ) > 0:
                    retval = True
                return retval

            game = Game.objects.filter(
                    player_second=current_user.id
                ).exclude(status=2)

            if len(game) == 0:
                game = Game.objects.filter(player_first=current_user.id)

            if len(game) > 0:



                try:
                    player_first_name = User.objects.get(id=game[0].player_first).username
                except User.DoesNotExist:
                    player_first_name = ""

                try:
                    player_second_name = User.objects.get(id=game[0].player_second).username
                except User.DoesNotExist:
                    player_second_name = ""

                is_your_move = False
                game_result = -1

                if game[0].user_message == "0":
                    if str(request.user) == str(player_second_name):
                        is_your_move = True

                elif not (user_is_logged(game[0].player_first) and user_is_logged(game[0].player_second)):
                    game[0].user_message = "1"
                    game[0].status = 4
                    game[0].save()

                elif len(game[0].user_message) > 0:

                    game_result = game_logic(game[0].user_message)

                    is_your_move = False

                    # second user win
                    if game_result == 1:
                        pass

                    # first user win
                    elif game_result == 2:
                        pass

                    # draw
                    elif game_result == 0:
                        pass

                    # continue game
                    elif game_result == -1:

                        pos_zero = game[0].user_message.rfind("o")
                        pos_cross = game[0].user_message.rfind("x")

                        if pos_cross > pos_zero:
                            logger.debug("Player second was moved. Current user is {:s}".format(str(request.user)))
                            if str(request.user) == str(player_second_name):
                                is_your_move = False
                            else:
                                is_your_move = True

                        elif pos_zero > pos_cross:
                            logger.debug("Player first was moved. Current user is {:s}".format(str(request.user)))
                            if str(request.user) == str(player_first_name):
                                is_your_move = False
                            else:
                                is_your_move = True


                data = {"game_id": game[0].id,
                        'player_first_name': player_first_name,
                        'player_second_name': player_second_name,
                        'game_status': game[0].status,
                        'user_message': game[0].user_message,
                        'is_your_move': is_your_move,
                        'game_result': game_result,
                        }
            else:
                data = {"game_id": 0}

            return HttpResponse(json.dumps(data))

        except User.DoesNotExist:
            raise Http404


class StatusGame(View):

    def get(self, request, game_id):
        if not request.user.is_authenticated():
            return HttpResponseUnauthorized()

        data = {}

        if not game_id.isdigit():
            raise Http404
        try:
            game = Game.objects.get(id=int(game_id))
            player_first_name = User.objects.get(id=game.player_first).username
            player_second_name = User.objects.get(id=game.player_second).username
            data = {'game_id': game.id, 'player_first_name': player_first_name, 'player_second_name': player_second_name, 'game_status': game.status, 'user_message': game.user_message}
        except Game.DoesNotExist:
            raise Http404

        return HttpResponse(json.dumps(data))


class SetGame(View):

    def post(self, request):
        if not request.user.is_authenticated():
            return HttpResponseUnauthorized()

        response_data = {'code': 0, 'msg': 'ok'}

        if request.POST['gameUserMessage'] == "1": # delete game
            try:
                game = Game.objects.get(id=request.POST['gameId'])
                game.delete()
            except Game.DoesNotExist:
                response_data = {'code': 1, 'msg': 'game not found'}

        elif request.POST['gameStatus'] == "0": # waiting for game
            try:
                game = Game.objects.get(id=request.POST['gameId'])
                game.status = int(request.POST['gameStatus'])
                if len(request.POST['gameUserMessage']) > 0:
                    game.user_message = int(request.POST['gameUserMessage'])
                game.save()
            except Game.DoesNotExist:
                response_data = {'code': 1, 'msg': 'game not found'}

        elif request.POST['gameStatus'] == "1": # accept game
            try:
                game = Game.objects.get(id=request.POST['gameId'])
                game.status = int(request.POST['gameStatus'])
                if len(request.POST['gameUserMessage']) > 0:
                    game.user_message = request.POST['gameUserMessage']
                game.save()
            except Game.DoesNotExist:
                response_data = {'code': 1, 'msg': 'game not found'}

        elif request.POST['gameStatus'] == "2": # reject game
            try:
                game = Game.objects.get(id=request.POST['gameId'])
                game.status = int(request.POST['gameStatus'])
                if len(request.POST['gameUserMessage']) > 0:
                    game.user_message = int(request.POST['gameUserMessage'])
                game.save()
            except Game.DoesNotExist:
                response_data = {'code': 1, 'msg': 'game not found'}

        elif request.POST['gameStatus'] == "4": # leave game
            try:
                game = Game.objects.get(id=request.POST['gameId'])
                game.status = int(request.POST['gameStatus'])
                if len(request.POST['gameUserMessage']) > 0:
                    game.user_message = request.POST['gameUserMessage']
                game.save()
            except Game.DoesNotExist:
                response_data = {'code': 1, 'msg': 'game not found'}

        return HttpResponse(json.dumps(response_data))


class ActiveUsers(View):
    """Returns all logged users with them status except for superuser
    """

    def get(self, request):
        if not request.user.is_authenticated():
            return HttpResponseUnauthorized()

        def get_username(session):
            userstatus = 0 # free by default
            u = User.objects.get(id=session.get_decoded()['_auth_user_id'])
            current_game = Game.objects.filter(
                player_second=u.id).exclude(status=2)
            if len(current_game) == 0:
                current_game = Game.objects.filter(
                player_first=u.id).exclude(status=2)
            if len(current_game) == 1:
                userstatus = 1 # in game
            return {'username': u.username, 'userstatus': userstatus}

        sessions = list(filter(lambda s: "_auth_user_id" in s.get_decoded(), Session.objects.filter(expire_date__gte=datetime.now())))
        data = list(map(get_username, sessions))

        # check for superuser
        def remove_superuser(user):
            retval = True
            if User.objects.get(username=user['username']).is_superuser:
                retval = False
            return retval

        data = list(filter(remove_superuser, data))

        return HttpResponse(json.dumps(data))


class InviteUser(View):
    """Create new game and returns game id
    """

    def post(self, request):
        if not request.user.is_authenticated():
            return HttpResponseUnauthorized()

        try:
            logger.debug("Invite for user: {:s}".format(request.POST["invitetouser"]))
            game = Game()
            game.player_first = User.objects.get(username=request.user).id
            game.player_second = User.objects.get(username=request.POST["invitetouser"]).id
            game.save()
            data = {'game_id': game.id}
        except User.DoesNotExist:
            raise Http404

        return HttpResponse(json.dumps(data))


class Index(View):

    def do_login(self, request):
        user = None
        if ("username" in request.POST) and ("password" in request.POST):
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
        retval = False
        if user is not None:
            logger.debug(user)
            if user.is_active:
                logger.debug("User {:s} is active".format(user.username))
                u = User.objects.get(username=user)
                logger.debug("{:s} {:s} {:d}".format(user.username, u.username, u.id))
                def is_same_user(session):
                    retval = False
                    if "_auth_user_id" in session.get_decoded():
                        if int(session.get_decoded()["_auth_user_id"]) == int(u.id):
                            retval = True
                    return retval
                curr_sessions = list(filter(is_same_user, Session.objects.all()))
                logger.debug(curr_sessions)
                list(map(lambda s: s.delete(), curr_sessions))
                login(request, user)
                retval = True
        return retval

    def post(self, request):

        retval = redirect("/index/")

        if not request.user.is_authenticated():
            if not self.do_login(request):
                return redirect("/index?login_error")

        return retval

    def get(self, request):

        template_data = {}
        template_file = "eng_index.html"
        cookie_lang = None

        (template_file, cookie_lang) = get_template_by_lang(request)

        if request.user.is_authenticated():

            template_data['login_success'] = True
            template_data['username'] = request.user

            if cookie_lang:
                try:
                    user_profile = UserProfile.objects.get(user=request.user)
                    user_profile.language = cookie_lang
                    user_profile.save()
                except UserProfile.DoesNotExist:
                    logger.debug("User profile not found")
                    pass

            else:
                try:
                    user_profile = UserProfile.objects.get(user=request.user)
                    cookie_lang = user_profile.language
                    if user_profile.language == 'rus':
                        template_file = "rus_index.html"
                    elif user_profile.language == 'eng':
                        template_file = "eng_index.html"
                except UserProfile.DoesNotExist:
                    pass

        else:
            template_data['login_required'] = True
            if "login_error" in request.GET:
                template_data['login_error'] = True

        response = render(request, template_file, template_data)

        if cookie_lang:
            response.set_cookie("lang", cookie_lang)

        return response


class Default(View):

    def get(self, request):
        return redirect("/index/")

    def post(self, request):
        return redirect("/index/")
