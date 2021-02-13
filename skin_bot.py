# skin cache bot

# imports
import requests
import time
from requests_toolbelt.multipart.encoder import MultipartEncoder

# authenticate a Mojang user
def authenticate(email, password):
    url = "https://authserver.mojang.com/authenticate" # endpoint
    payload = { # json payload
        "agent": {
            "name": "Minecraft",
            "version": 1
        },
        "username": email,
        "password": password,
        "clientToken": "skinChange"
    }
    headers = {"Content-Type": "application/json"} # headers
    r = requests.post(url, headers=headers, json=payload) # fire off request
    print(f"[authenticate]: {r.status_code}") # debug
    if r.status_code == 200: # valid session
        json_data = r.json()
        return json_data["accessToken"] # get bearer token
    else:
        return "error" # pain.

# refresh an access token
def refresh(email, password, bearer):
    url = "https://authserver.mojang.com/refresh" # endpoint
    payload = { # json payload
        "accessToken": bearer,
        "clientToken": "skinChange"
    }
    headers = {"Content-Type": "application/json"} # headers
    r = requests.post(url, headers=headers, json=payload) # fire off request
    print(f"[refresh]: {r.status_code}") # debug
    if r.status_code == 200: # valid session
        json_data = r.json()
        return json_data["accessToken"] # get new bearer token
    else:
        token = authenticate(email, password)
        if token != "error":
            return token
        else:
            return "error" # pain.

# cache a skin on NameMC
def cache_skin(profile_url, username):
    url = profile_url # NameMC profile URL
    headers = { # headers - avoid cloudflare detection
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": f"https://namemc.com/search?q={username}", # needed apparently
        "Connection": "keep-alive",
        "Cookie": "",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
        "TE": "Trailers",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0"
    }
    r = requests.get(url, headers=headers) # fire off request
    print(f"[cache]: {r.status_code}") # debug

# change the skin
def change_skin(skin_file, variant, bearer, base_path, email, password):
    print(f"changing to {skin_file.replace(base_path, '')}")
    url = "https://api.minecraftservices.com/minecraft/profile/skins" # endpoint
    mp_encoder = MultipartEncoder(
        fields={
            "variant": variant,
            # plain file object, no filename or mime type produces a
            # Content-Disposition header with just the part name
            "file": (skin_file, open(skin_file, "rb"), "image/png"),
        }
    )
    headers = { # headers
        "Authorization": f"Bearer {bearer}", # authorize the user
        "Content-Type": mp_encoder.content_type
    }
    r = requests.post(url, headers=headers, data=mp_encoder) # fire off request
    print(f"[change_skin]: {r.status_code}") # debug
    if r.status_code != 200:
        print("error changing skin, waiting and refreshing")
        print(r.text)
        time.sleep(30)
        bearer = refresh(email, password, bearer)
        change_skin(skin_file, "slim", bearer, base_path, email, password)

# generate skin URLs
def get_skins(base_path, number_of_skins):
    skins = []
    for i in range(0, number_of_skins): # loop through desired number of skins
        skins.append(f"{base_path}skins-{i}.png")
    return skins # return array

# main script
def main():
    print("skin bot")
    base_path = input("enter base folder path INCLUDING trailing / (e.g \"cat.png-sameskin/\"): ")
    number_of_skins = int(input("how many skins do you have? "))
    profile_url = input("enter NameMC profile URL: ")
    username = input("enter username: ")
    email = input("enter account email: ")
    password = input("enter account password: ")
    cache_time = int(input("enter cache time in sec: "))
    skins_cached = 0 # number of skins we have cached
    bearer = authenticate(email, password) # get token

    if bearer != "error": # not pain
        while True: # always loop
            skins = get_skins(base_path, number_of_skins) # get the array
            for skin in skins: # loop through skins
                change_skin(skin, "slim", bearer, base_path, email, password) # change the skin
                time.sleep(cache_time) # sleep to avoid unnecessary hitting namemc
                cache_skin(profile_url, username) # cache the skin
                skins_cached += 1 # add to total
                bearer = refresh(email, password, bearer) # refresh bearer token
                if bearer == "error": # pain.
                    break

main() # run program
