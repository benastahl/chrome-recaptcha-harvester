from django.shortcuts import render
import os
import sys
file_dividers = None

# Operating system adaptation

if sys.platform == "darwin":
    # OS X
    file_dividers = "/"

elif sys.platform == "win32":
    # Windows
    file_dividers = "\\"

elif sys.platform.startswith("linux"):
    # Linux
    file_dividers = "/"

# Create your views here.
template_dir = os.path.dirname(os.path.dirname(__file__)) + file_dividers + "server_app" + file_dividers + "templates" + file_dividers + "server_app" + file_dividers


def waiting_for_captcha(response):
    print("LAUNCHING WFC HTML RESPONSE...")
    print(template_dir)
    return render(response, template_dir + "waiting.html", {})


def load(response):
    return render(response, template_dir + "startup_load.html", {})
