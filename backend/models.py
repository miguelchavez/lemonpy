from django.db import models
from django.contrib.auth.models import User

#if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    #os.environ['DJANGO_SETTINGS_MODULE']='settings'
    


#Extendiendo el model Users
User.add_to_class('address', models.TextField(blank=False))
User.add_to_class('phone', models.CharField(blank=True, max_length=30)) #NOTE: make it USPhoneField ???

