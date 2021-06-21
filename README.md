# Chrome Captcha Harvester

#### **The harvester allows you to collect `g_recaptcha_tokens` for use in your projects.**
### Discord
If you have questions or need help setting up, please join the discord [here][https://discord.gg/xcjq3SM7].
### External libraries
##
- selenium
- selenium-wire
- PyInquirer
- colorama
- django
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

### Chrome Login
#### The `Chrome Login` feature allows you to login to your gmail accounts and save them as browser profiles for later use.




[]: https://discord.gg/xcjq3SM7