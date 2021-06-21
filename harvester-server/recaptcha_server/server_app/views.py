from django.shortcuts import render
import os

# Create your views here.
template_dir = os.path.dirname(os.path.dirname(__file__)) + "\\server_app\\templates\\server_app\\"


def waiting_for_captcha(response):
    print("LAUNCHING WFC HTML RESPONSE...")
    print(template_dir)
    return render(response, template_dir + "waiting.html", {})


def load(response):
    return render(response, template_dir + "startup_load.html", {})
