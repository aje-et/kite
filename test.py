import requests
import pyotp
import logging
import json
from kiteconnect import KiteConnect


with open("login_credentials.json", "r") as file:
    login_credentials = json.load(file)
    
kite = KiteConnect(login_credentials["api_key"])

url = kite.login_url()
print(url)

# request_token = ""
request_token = None
if request_token is None:
    import pdb; breakpoint()
    
session_data = kite.generate_session(request_token, login_credentials["api_secret"])



# with open("session.json", "w") as file:
#     file.write(json.dumps({"access_token": session_data["access_token"], "refresh_token": session_data["refresh_token"], "enctoken": session_data["enctoken"], "public_token": session_data["public_token"]}))

