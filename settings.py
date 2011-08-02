# -*- coding: utf-8 -*-
#DEFAULT_CHARSET='utf-8'

import os.path

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'datos_plaza',                # Or path to database file if using sqlite3.
        'USER': 'miguel',               # Not used with sqlite3. TODO: USAR un nombre que no sea predecible.
        'PASSWORD': 'xarwit0721',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Mexico_City'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
#NOTE: Si pongo 'es-MX' NO lo toma en cuenta. Pone los numeros en formato europeo ( 1.500,00 ).
#      Tal vez el es-MX es copy/paste del es-ES (o solo es) porque en España se usa el punto como separador de miles.
LANGUAGE_CODE = 'es-MX'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True



INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.humanize',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'plaza',
)

NUMBER_GROUPING=3
THOUSAND_SEPARATOR = ','
USE_THOUSAND_SEPARATOR = True
DECIMAL_SEPARATOR ='.'
#https://docs.djangoproject.com/en/dev/topics/i18n/localization/
FORMAT_MODULE_PATH='formats'