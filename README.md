# Chrome Captcha Harvester
####_Created by Volt#9540_

#### **The harvester allows you to collect `g_recaptcha_tokens` for use in your projects.**
### Discord
If you have questions or need help setting up, please join the discord [here](https://discord.gg/2u2qCTXas5).
##
### External libraries
##
- selenium
- selenium-wire
- PyInquirer
- colorama
- django

### Notes:
##
- You may need to update chromedriver if out of date. 
- Localhost is enabled (True) as default.
- token_count (the amount of valid recaptcha tokens you want) is set to 1 as default.
## Setup

### Step 1:
- Download the project files by either cloning or downloading the zip file via GitHub.
- Install all external libraries using `pip install {lib}` in your venv (virtual environment).

### Step 2a (server setup):
In cmd or your IDE, enter the `harvester-server\\recaptcha_server` directory (`harvester-server/recaptcha_server` if you are using mac).
##### In CMD:
`cd {path to recaptcha_server dir}`
#### In IDE (inside `chrome-recaptcha-harvester` dir):
`cd harvester-server\\recaptcha_server`

### Step 2b (server setup):
In terminal: `python manage.py runserver`

This will start your local Django server, which the harvester uses to create a "Waiting for Captcha" page.

##
### Chrome Login
#### The `Chrome Login` feature allows you to login to your gmail accounts and save them as browser profiles for later use.
From the menu:
- Select `Chrome Login`
- Enter the desired profile name.
- Login to your gmail account
- Congrats! Your gmail account is saved.
