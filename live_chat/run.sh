#!/bin/bash

export DJANGO_SETTINGS_MODULE=live_chat.settings
echo "Starting Daphne server with DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE"
daphne -b 127.0.0.1 -p 8000 live_chat.asgi:application
