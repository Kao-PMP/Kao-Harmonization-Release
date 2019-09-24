#!/usr/bin/env python3

from django import db
from django.db import connection
from django.conf import settings
import django

settings.configure()
django.setup()
print(db.connections.databases)
print(connection.settings_dict)

