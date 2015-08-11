#!/bin/bash
if [ -z "$VCAP_APP_PORT" ];
then SERVER_PORT=3000;
else SERVER_PORT="$VCAP_APP_PORT";
fi
echo port is $SERVER_PORT
python manage.py runserver --noreload 0.0.0.0:$SERVER_PORT
echo Running san-francisco-life