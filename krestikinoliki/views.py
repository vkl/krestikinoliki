'''
Created on 2 september 2015
@author: vkl
'''

from django.shortcuts import render, redirect
from django.shortcuts import HttpResponse, Http404
from django.http.response import HttpResponseNotFound
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session

#from krestikinoliki.models import Sensor, Location
from krestikinoliki.forms import LoginForm
from settings import BASE_DIR, APP_NAME

import logging
import json
import os

from pip._vendor import requests
from pip._vendor.requests.packages.urllib3.util import request
from test.test_urllib2 import RequestTests
from _sqlite3 import IntegrityError
from krestikinoliki.models import Game

LOG_FILE = os.path.join(BASE_DIR, "{:s}.log".format(APP_NAME))

logger = logging.Logger("krestikinoliki")
#fileHd = logging.FileHandler(LOG_FILE)
streamHd = logging.StreamHandler()
#logger.addHandler(fileHd)
logger.addHandler(streamHd)

# Create your views here.

def do_login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    retval = False
    if user is not None:
        logger.debug(user)
        if user.is_active:
            logger.debug("User {:s} is active".format(user))
            u = User.objects.get(username=user)
            logger.debug("{:s} {:s} {:d}".format(user, u.username, u.id))
            curr_sessions = filter(lambda s: int(s.get_decoded()['_auth_user_id']) == int(u.id), Session.objects.all())
            logger.debug(curr_sessions)
            map(lambda s: s.delete(), curr_sessions)
            login(request, user)
            update_session_auth_hash(request, user)
            retval = True
    return retval

def do_logout(request):
    # remove all games for user
    u = User.objects.get(username=request.user)
    games = Game.objects.filter(player_first=u.id)
    map(lambda x: x.delete(), games)
    games = Game.objects.filter(player_second=u.id)
    map(lambda x: x.delete(), games)
    logout(request)
    return redirect("/index/")

def do_registry(request):
    if request.method == "GET":
        logger.debug("Registry required")
        retval = render(request, "index.html", {'registration_required': True})
    elif request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        try:
            logger.debug("Try to create user")
            user = User.objects.create_user(username=username, password=password)
            user.save()
            logger.debug("Registry success")
            retval = redirect("/index/")
        except Exception as e:
            logger.error("Could not create user. Error {:s}".format(e))
            retval = render(request, "index.html", {'registration_required': True, 'user_error': username})
    return retval

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
    r = map(check, g)
    # vertical
    r.extend(map(check, [[g[0][0], g[1][0], g[2][0]], [g[0][1], g[1][1], g[2][1]], [g[0][2], g[1][2], g[2][2]]]))
    # diagonal
    r.extend(map(check, [[g[0][0], g[1][1], g[2][2]], [g[2][0], g[1][1], g[0][2]]]))
    res = filter(lambda x: x == 1, r)
    if len(res) > 0:
        return 1 
    res = filter(lambda x: x == 2, r)
    if len(res) > 0:
        return 2
    res = filter(lambda x: x == -1, r)
    if len(res) > 0:
        return -1
    return 0
    

def status_user(request):
    if not request.user.is_authenticated():
        raise Http404
    
    if request.method == "GET":
        try:
            
            current_user = User.objects.get(username=request.user)
            game = Game.objects.filter(player_second=current_user.id)
            d = json.JSONEncoder()
            
            if len(game) == 0:
                game = Game.objects.filter(player_first=current_user.id)
                
            if len(game) > 0:
                
                player_first_name = User.objects.get(id=game[0].player_first).username
                player_second_name = User.objects.get(id=game[0].player_second).username
                
                is_your_move = False
                game_result = -1
                
                if game[0].user_message == "0":
                    if str(request.user) == str(player_second_name):
                        is_your_move = True
                        
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
            json_data = d.encode(data)
            return HttpResponse(json_data)
        
        except User.DoesNotExist:
            raise Http404
    

def status_game(request, game_id):
    if not request.user.is_authenticated():
        raise Http404
    
    d = json.JSONEncoder()
    data = {}
    
    if request.method == "GET":
        if not game_id.isdigit:
            raise Http404
        try:
            game = Game.objects.get(id=int(game_id))
            player_first_name = User.objects.get(id=game.player_first).username
            player_second_name = User.objects.get(id=game.player_second).username
            data = {'game_id': game.id, 'player_first_name': player_first_name, 'player_second_name': player_second_name, 'game_status': game.status, 'user_message': game.user_message}
        except Game.DoesNotExist:
            raise Http404
        
    json_data = d.encode(data)
    return HttpResponse(json_data)

def set_game(request):
    if not request.user.is_authenticated():
        raise Http404
    
    if request.method == "POST":
        d = json.JSONEncoder()
        
        if request.POST['gameUserMessage'] == "1": # delete game
            try:
                game = Game.objects.get(id=request.POST['gameId'])
                game.delete()
            except game.DoesNotExist:
                raise Http404
            
        elif request.POST['gameStatus'] == "2": # reject game
            try:
                game = Game.objects.get(id=request.POST['gameId'])
                game.status = int(request.POST['gameStatus'])
                if len(request.POST['gameUserMessage']) > 0:
                    game.user_message = int(request.POST['gameUserMessage'])
                game.save()
            except game.DoesNotExist:
                raise Http404
            
        elif request.POST['gameStatus'] == "1": # accept game
            try:
                game = Game.objects.get(id=request.POST['gameId'])
                game.status = int(request.POST['gameStatus'])
                if len(request.POST['gameUserMessage']) > 0:
                    game.user_message = request.POST['gameUserMessage']
                game.save()
            except game.DoesNotExist:
                raise Http404
            
        json_data = d.encode({'msg': 'ok'})
        return HttpResponse(json_data)
    else:
        raise Http404
            
    

def active_users(request):
    """Returns all logged users with them status except for superuser
    """
    if not request.user.is_authenticated():
        raise Http404
    d = json.JSONEncoder()
    
    def get_username(session):
        userstatus = 0 # free by default
        u = User.objects.get(id=session.get_decoded()['_auth_user_id'])
        current_game = Game.objects.filter(player_second=u.id)
        if len(current_game) == 0:
            current_game = Game.objects.filter(player_first=u.id)
        if len(current_game) == 1:
            userstatus = 1 # in game
        return {'username': u.username, 'userstatus': userstatus}
    
    data = map(get_username, Session.objects.all())
    
    # check for superuser
    def remove_superuser(user):
        retval = True
        if User.objects.get(username=user['username']).is_superuser:
            retval = False
        return retval
    
    data = filter(remove_superuser, data) 
    json_data = d.encode(data)
    return HttpResponse(json_data)

def invite_user(request):
    """Create new game and returns game id
    """
    if not request.user.is_authenticated():
        raise Http404
    if request.method == "POST":
        d = json.JSONEncoder()
        logger.debug("Invite for user: {:s}".format(request.POST["invitetouser"]))
        game = Game()
        game.player_first = User.objects.get(username=request.user).id
        game.player_second = User.objects.get(username=request.POST["invitetouser"]).id 
        game.save()
        data = {'game_id': game.id}
        json_data = d.encode(data)
        return HttpResponse(json_data)
    else:
        raise Http404
    
def index(request):
    logger.debug("Index")
    template_data = {}
    if not request.user.is_authenticated():
        if request.method == "POST":
            if do_login(request):
                logger.debug(request.user)
                template_data = {'login_success': True, 'username': request.user}
            else:
                logger.debug("Username and/or password are wrong")
                template_data = {'login_required': True, 'login_error': True}
        else:
            logger.debug("Login required")
            template_data = {'login_required': True}
    else:
        template_data['login_success'] = True
        template_data['username'] = request.user   

    return render(request, "index.html", template_data)
    

def default(request):
    return redirect("/index/")

