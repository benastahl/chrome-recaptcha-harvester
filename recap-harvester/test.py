import os
file_dividers = "\\"

dir_path = os.path.dirname(os.path.realpath(__file__))
browser_profile_dir = dir_path.replace('recap-harvester', 'browser-profiles' + file_dividers)

profile_name = "profilename"
browser_storage = browser_profile_dir + profile_name
profile_list = str(os.listdir(browser_profile_dir))
print(browser_storage)
print(profile_list)
