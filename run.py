#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freshtrack_project.settings')
django.setup()

from django.core.management import call_command
call_command('runserver', '0.0.0.0:8000')
