from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django_ajax.decorators import ajax
from requests.auth import HTTPBasicAuth
import json
import requests
import logging
from . import form

logging.basicConfig()

def new(request):
    return render(request, 'dashboard.html')

@ajax
def watson(request):
    headers = {
        'content-type':'application/json'
    }
    # Replace the username,password and url with the credentials from VCAP_SERVICES
    USERNAME = 'USERNAME'
    PASSWORD = 'PASSWORD'
    URL = 'SERVICE_URL'

    auth = HTTPBasicAuth(USERNAME, PASSWORD)
    response = requests.post(URL + '/v1/dilemmas', data=request.body, headers=headers, auth=auth)
    results = json.loads(response.text)
    return results