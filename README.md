# Chrome ReCaptcha Harvester
_Created by Volt#9540_

***
#### **This project allows you to open multiple chrome harvesters with your chrome profiles, and call for a `g_recaptcha_token` for use in your own project. The harvester is compatible with both ReCaptcha V2 and ReCaptcha V3. It is capable of one-clicks on V2 and 0.9 scores on V3.**
### Support
If you have questions or need help setting up, please join the discord [here](https://discord.gg/2u2qCTXas5).

***
## Setup
#### 1. Install Requirements
Install all project requirements with `pip3 install -r requirements.txt` 
#### 2. Chrome Login
The `chrome_login` function only needs to called once for each profile you want to create. If you attempt to call it twice with the same `profile_name`, it will send an error. Once called, a browser will open where you will log-in to your chrome account.`chrome_login` takes in 2 arguments:
- `profile_name`: which can be anything that meet file name formatting.
- `proxy`: _Optional_. This is, by default, set to off. Meaning if you don't fill in the argument, the harvester will use `localhost` (or your own ip address). Argument format: `host:port:username:password`.

```python
chrome_login(profile_name="Your super cool profile", proxy="oogabooga.com:10101:jon:smith")
```
or (localhost)
```python
chrome_login(profile_name="Your super cool profile")
```


#### 3. Open Harvester
Open your harvester simply by calling the `open_harvester` with the `profile_name` you want to open the harvester with. Once called, a browser will open with a `Waiting for Captcha` page. This harvester is now on standby for any `harvest_token` function calls.
```python
open_harvester(profile_name="Your super cool profile")
```

#### 4. Call for token
To call for a `g_recaptcha_token`, simply call the `harvest_token` function with the captcha type and URL of the captcha location.

ReCaptcha V2:
```python
g_recaptcha_token = harvest_token(captcha_type="v2", url="https://www.google.com/recaptcha/api2/demo")
```
ReCaptcha V3 (Invisible):
```python
g_recaptcha_token = harvest_token(captcha_type="v3", url="https://tech.aarons.com/")
```
When called, a request will be put into a queue for the next available harvester for you to solve. Once solved, the function will return the `g_recaptcha_token`
***
### NOTES
* The harvester is completely thread-safe. It is compatible with running high numbers of multi-threaded tasks.
* When calling `harvest_token` with ReCaptcha V3 (`v3`), there will be a pause in between when the token is grabbed and when the page is fully loaded. **This is normal.** It is simply waiting for the V3 token to be generated.
***
## Examples
Simple Example
```python
from harvester import chrome_login, open_harvester, harvest_token

if __name__ == '__main__':
    # Creates browser profile after login. Should only be called once with same profile name.
    chrome_login(profile_name="Your cool profile")

    # Opens the harvester. Once opened, harvester waits for harvest_token call.
    open_harvester(profile_name="Your cool profile")
    
    harvest_token(captcha_type="v2", url="https://www.google.com/recaptcha/api2/demo")
    harvest_token(captcha_type="v3", url="https://tech.aarons.com/")

```
Threading Example (multiple harvest_token calls at once)
```python
from harvester import chrome_login, open_harvester, harvest_token
import threading

if __name__ == '__main__':
    # Creates browser profile after login. Should only be called once with same profile name.
    chrome_login(profile_name="Your cool profile")

    # Opens the harvester. Once opened, harvester waits for harvest_token call.
    open_harvester(profile_name="Your cool profile")
    
    # V3 (invisible) calls
    for _ in range(3):
        threading.Thread(target=harvest_token, args=("v3", "https://tech.aarons.com/")).start()
    
    # V2 calls
    for _ in range(3):
        threading.Thread(target=harvest_token, args=("v2", "https://www.google.com/recaptcha/api2/demo")).start()

```
***
