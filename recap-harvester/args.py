from selenium.webdriver.chrome.options import Options


class ProfileArguments:
    opts = Options()
    opts.add_argument('--allow-insecure-localhost')
    opts.add_argument('--ignore-ssl-errors')
    opts.add_argument('--ignore-certificate-errors-spki-list')
    opts.add_argument('--ignore-certificate-errors')
    opts.add_argument("user-agent=Chrome")
    opts.add_argument("--disable-blink-features")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)
    opts.add_argument('--disable-extensions')
    opts.add_argument('disable-infobars')
    opts.add_argument('--window-size=500,645')
    opts.add_argument('--allow-profiles-outside-user-dir')
    opts.add_experimental_option('excludeSwitches', ['enable-logging'])