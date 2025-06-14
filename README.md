
---

# Chrome reCAPTCHA Harvester  
_Created by mr.appa (Discord)_

---

## Overview

This project allows you to spawn multiple Chrome-based CAPTCHA harvesters using custom Chrome profiles. It can solve both **reCAPTCHA v2** (checkbox) and **reCAPTCHA v3** (invisible), returning a valid `g_recaptcha_token` for use in your own automation workflows.

- ✅ One-clicks on **reCAPTCHA v2**
- ✅ High (0.9+) scores on **reCAPTCHA v3**
- ✅ Fully thread-safe
- ✅ Supports proxies with auth
- ✅ Uses real Chrome profiles (boosts trust score)

> **Need help?** Join the support [discord](https://discord.gg/2u2qCTXas5)

---

## ⚙️ Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
````

---

### 2. Create a Chrome Profile

```python
from harvester import chrome_login

chrome_login(profile_name="MyCoolProfile")
```

This opens a new Chrome window. Log into your Google account (e.g., Gmail). The profile is saved for future use.

> ✅ Only needs to be done **once** per profile.
> 
> ❌ Will raise an error if the same profile name is reused.

Optional with proxy:

```python
chrome_login(profile_name="MyCoolProfile", proxy="host:port:user:pass")
```

---

### 3. Start a Harvester

```python
from harvester import open_harvester

open_harvester(profile_name="MyCoolProfile")
```

> A browser window will open and display "Waiting for Captcha". It's now ready to receive harvesting tasks.

---

### 4. Harvest Tokens

```python
from harvester import harvest_token

# reCAPTCHA v2
token = harvest_token(captcha_type="v2", captcha_url="https://www.google.com/recaptcha/api2/demo")

# reCAPTCHA v3 (invisible)
token = harvest_token(captcha_type="v3", captcha_url="https://tech.aarons.com/")
```

---

## ⚠️ Notes

* ✅ **Thread-safe** — supports high concurrency via Python threads.
* 🕒 **V3 Tokens** may have a short delay after page load — this is normal and expected.
* 🔒 **Proxy Support** — format: `host:port:user:pass`

---

## 🧪 Examples

### 🔹 Basic Usage

```python
from harvester import chrome_login, open_harvester, harvest_token

if __name__ == '__main__':
    chrome_login(profile_name="MyCoolProfile")
    open_harvester(profile_name="MyCoolProfile")

    v2_token = harvest_token(captcha_type="v2", captcha_url="https://www.google.com/recaptcha/api2/demo")
    v3_token = harvest_token(captcha_type="v3", captcha_url="https://tech.aarons.com/")
```

---

### 🔹 Multi-threaded Token Harvesting

```python
import threading
import harvester
import uuid
import time


if __name__ == '__main__':
    # login to your chrome account
    harvester.chrome_login("YourCoolProfile")
    
    # open the harvester (waiting for captcha page)
    harvester.open_harvester("YourCoolProfile")
    
    # synchronous call example
    synch_token = harvester.harvest_token("v2", "https://www.google.com/recaptcha/api2/demo")
    print(
        f"""
            Task ID:            {synch_token.task_id}
            Token Value:        {synch_token.g_recaptcha_token[0:30]}...
            Captcha URL:        {synch_token.captcha_url}
            Captcha Type:       {synch_token.captcha_type}
            Proxy Used:         {synch_token.proxy_used}
            Profile Used:       {synch_token.profile_used}
            Expiry Datetime:    {synch_token.expiry_datetime}
            Expired:            {synch_token.expired}
            Ingested:           {synch_token.ingested}
            """
    )    
    # generate task id strings (could be anything) to keep track of the tokens you request
    task_number = 5
    v2_task_ids = [str(uuid.uuid4()) for _ in range(task_number)]

    threads = []
    
    # request tokens from the harvester (change to "v3" for v3)
    for task_id in v2_task_ids:
        t = threading.Thread(target=harvester.harvest_token, args=("v2", "https://www.google.com/recaptcha/api2/demo", task_id,))
        t.start()
        threads.append(t)
    
    # wait for the tokens to finish (can be handled differently depending on what you want to do)
    tokens = []
    for task_id in v2_task_ids:
        
        # wait for token to be harvested by user
        while not harvester.token_ready(task_id):
            time.sleep(0.5)
        
        token = harvester.get_token_safely(task_id)
        tokens.append(token)
    
    # wait for all threads to end
    for t in threads:
        t.join()

    for token in tokens:
        print(
            f"""
            Task ID:            {token.task_id}
            Token Value:        {token.g_recaptcha_token[0:30]}...
            Captcha URL:        {token.captcha_url}
            Captcha Type:       {token.captcha_type}
            Proxy Used:         {token.proxy_used}
            Profile Used:       {token.profile_used}
            Expiry Datetime:    {token.expiry_datetime}
            Expired:            {token.expired}
            Ingested:           {token.ingested}
            """
        )
```

---

## 📦 Token Object Structure

When you call `harvest_token(...)`, it returns a `Token` object containing metadata and the harvested CAPTCHA token.

```python
token = harvest_token("v2", "https://www.google.com/recaptcha/api2/demo")
print(token.g_recaptcha_token)
```

### 🔍 Token Fields

| Field               | Type                 | Description                                                           |
| ------------------- | -------------------- | --------------------------------------------------------------------- |
| `task_id`           | `str`                | Unique identifier for the CAPTCHA task.                               |
| `captcha_url`       | `str`                | The URL where the CAPTCHA challenge was solved.                       |
| `captcha_type`      | `str`                | CAPTCHA type (`"v2"` or `"v3"`).                                      |
| `g_recaptcha_token` | `Optional[str]`      | The solved CAPTCHA token returned by Google.                          |
| `profile_used`      | `Optional[str]`      | The Chrome profile name used for solving the CAPTCHA.                 |
| `proxy_used`        | `Optional[str]`      | The proxy (if any) that was used during CAPTCHA solving.              |
| `expiry_datetime`   | `Optional[datetime]` | Timestamp when the token was generated.                               |
| `expired`           | `bool`               | `True` if more than 2 minutes have passed since the token was issued. |
| `ingested`          | `bool`               | `True` if token has entered the harvester. Really only for internal   |

### ✅ Example

```python
print(token.task_id)
print(token.captcha_type)
print("Token:", token.g_recaptcha_token)
print("Expired?", token.expired)
```


---

## 📁 Project Structure

```
harvester/
├── harvester.py               # Main module
├── _utils.py                  # Utility functions for Chrome profiles and proxy config
├── chromedrivers/             # Automatically managed Chromedriver binaries
└── requirements.txt
```

---

## 📬 Questions?

For support, bug reports, or suggestions, [join the Discord](https://discord.gg/2u2qCTXas5) or open an issue in the repository.

---

```example output
(venv) benastahl@Bens-MacBook-Pro chrome-recaptcha-harvester % python3 main.py
[06-14-2025 14:57:10] - [2] - [Captcha Harvester] - Token in need! Grabbing one (3eb09727-276b-4336-ac04-9ac4782b4ff0)...
[06-14-2025 14:57:10] - [1] - [Captcha Harvester] - Token in need! Grabbing one (7b629dad-0664-4c79-ba01-f93d62e971b2)...
[06-14-2025 14:57:11] - [2] - [Captcha Harvester] - Waiting for Captcha...
[06-14-2025 14:57:11] - [1] - [Captcha Harvester] - Waiting for Captcha...
[06-14-2025 14:57:13] - [1] - [Captcha Harvester] - Valid token found
[06-14-2025 14:57:13] - [1] - [Captcha Harvester] - Token in need! Grabbing one (8bf444ae-ce87-46a4-abad-ff7f1477f0b8)...
[06-14-2025 14:57:13] - [1] - [Captcha Harvester] - Waiting for Captcha...
[06-14-2025 14:57:14] - [2] - [Captcha Harvester] - Valid token found
[06-14-2025 14:57:14] - [2] - [Captcha Harvester] - Token in need! Grabbing one (ecf6b6f5-030e-48d6-b118-02213e4cc00a)...
Task (3eb09727-276b-4336-ac04-9ac4782b4ff0) received token
Task (7b629dad-0664-4c79-ba01-f93d62e971b2) received token
[06-14-2025 14:57:15] - [2] - [Captcha Harvester] - Waiting for Captcha...
[06-14-2025 14:57:15] - [1] - [Captcha Harvester] - Valid token found
[06-14-2025 14:57:15] - [1] - [Captcha Harvester] - Token in need! Grabbing one (c85921c3-f8e7-4b74-86d1-418197101f73)...
Task (8bf444ae-ce87-46a4-abad-ff7f1477f0b8) received token
[06-14-2025 14:57:16] - [1] - [Captcha Harvester] - Waiting for Captcha...
[06-14-2025 14:57:16] - [2] - [Captcha Harvester] - Valid token found
Task (ecf6b6f5-030e-48d6-b118-02213e4cc00a) received token
[06-14-2025 14:57:17] - [1] - [Captcha Harvester] - Valid token found
Task (c85921c3-f8e7-4b74-86d1-418197101f73) received token

            Task ID:            7b629dad-0664-4c79-ba01-f93d62e971b2
            Token Value:        03AFcWeA7P...
            Captcha URL:        https://www.google.com/recaptcha/api2/demo
            Captcha Type:       v2
            Proxy Used:         None
            Profile Used:       YourCoolProfile
            Expiry Datetime:    2025-06-14 14:59:13.229878
            Expired:            False
            Ingested:           True
            

            Task ID:            8bf444ae-ce87-46a4-abad-ff7f1477f0b8
            Token Value:        03AFcWeA7Y...
            Captcha URL:        https://www.google.com/recaptcha/api2/demo
            Captcha Type:       v2
            Proxy Used:         None
            Profile Used:       YourCoolProfile
            Expiry Datetime:    2025-06-14 14:59:15.475580
            Expired:            False
            Ingested:           True
            

            Task ID:            ecf6b6f5-030e-48d6-b118-02213e4cc00a
            Token Value:        03AFcWeA4N...
            Captcha URL:        https://www.google.com/recaptcha/api2/demo
            Captcha Type:       v2
            Proxy Used:         None
            Profile Used:       New1
            Expiry Datetime:    2025-06-14 14:59:16.412794
            Expired:            False
            Ingested:           True
            

            Task ID:            c85921c3-f8e7-4b74-86d1-418197101f73
            Token Value:        03AFcWeA77...
            Captcha URL:        https://www.google.com/recaptcha/api2/demo
            Captcha Type:       v2
            Proxy Used:         None
            Profile Used:       YourCoolProfile
            Expiry Datetime:    2025-06-14 14:59:19.443647
            Expired:            False
            Ingested:           True
            

            Task ID:            3eb09727-276b-4336-ac04-9ac4782b4ff0
            Token Value:        03AFcWeA5A...
            Captcha URL:        https://www.google.com/recaptcha/api2/demo
            Captcha Type:       v2
            Proxy Used:         None
            Profile Used:       New1
            Expiry Datetime:    2025-06-14 14:59:14.383790
            Expired:            False
            Ingested:           True
```

