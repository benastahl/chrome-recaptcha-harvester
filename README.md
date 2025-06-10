
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

    harvest_token(captcha_type="v2", captcha_url="https://www.google.com/recaptcha/api2/demo")
    harvest_token(captcha_type="v3", captcha_url="https://tech.aarons.com/")
```

---

### 🔹 Multi-threaded Token Harvesting

```python
import threading
import harvester
import uuid
import time


def wait_for_token(task_id, timeout=60):
    start = time.time()
    while not harvester.token_ready(task_id):
        if time.time() - start > timeout:
            print(f"Timeout waiting for token {task_id}")
            return None
        time.sleep(0.5)
    return harvester.get_token_safely(task_id)


if __name__ == '__main__':
    harvester.open_harvester("New1")

    v2_task_ids = [str(uuid.uuid4()) for _ in range(1)]

    threads = []
    for task_id in v2_task_ids:
        t = threading.Thread(target=harvester.harvest_token, args=("v2", "https://www.google.com/recaptcha/api2/demo", task_id,))
        t.start()
        threads.append(t)

    v3_task_ids = [str(uuid.uuid4()) for _ in range(1)]

    for task_id in v3_task_ids:
        t = threading.Thread(target=harvester.harvest_token, args=("v3", "https://media.mbusa.com/", task_id,))
        t.start()
        threads.append(t)

    tokens = []
    for task_id in v2_task_ids:
        token = wait_for_token(task_id)
        tokens.append(token)

    for task_id in v3_task_ids:
        token = wait_for_token(task_id)
        tokens.append(token)

    for t in threads:
        t.join()

    print(tokens)

    for token in tokens:
        print(
            f"""
            Task ID:            {token.task_id}
            Captcha URL:        {token.captcha_url}
            Captcha Type:       {token.captcha_type}
            Proxy Used:         {token.proxy_used}
            Profile Used:       {token.profile_used}
            Expiry Datetime:    {token.expiry_datetime}
            Expired:            {token.expired}
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

