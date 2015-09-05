'''
Created on 2 september 2015

@author: vkl
'''

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Game(models.Model):
    STATUS_TYPE = (
        (0, 'Waiting'),
        (1, 'Accept'),
        (2, 'Reject'),
        (3, 'Over'),
    )
    player_first = models.IntegerField()
    player_second = models.IntegerField()
    status = models.IntegerField(choices=STATUS_TYPE, default=0)
    user_message = models.CharField(max_length=48, default="")
    