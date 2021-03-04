from flask import Flask, render_template, redirect, request, session, url_for
from urllib.parse import quote
import requests
import json

app = Flask(__name__)
app.secret_key = b'\xb5\xf0>npXE+\x96%\xa62\xc1b\x10\xde'


# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

# Server-side Parameters
CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 5000
REDIRECT_URI = "{}:{}/callback/q".format(CLIENT_SIDE_URL, PORT)
SCOPE = "playlist-modify-public playlist-modify-private user-modify-playback-state user-read-playback-state user-read-currently-playing user-library-modify user-read-recently-played"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()

# Client Keys
CLIENT_ID = "9ad9f0fd6b9845479eca819fe59b4a88"
CLIENT_SECRET = "93e5c861bc4640d4a1ad22e4ee47b4dc"

auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    "client_id": CLIENT_ID
}


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/auth")
def auth():
    url_args = "&".join(["{}={}".format(key, quote(val)) for key, val in auth_query_parameters.items()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    return redirect(auth_url)

@app.route("/callback/q")
def callback():
    # Auth Step 4: Requests refresh and access tokens

    auth_token = request.args['code']
    print("auth_token", auth_token)
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload)
    # Auth Step 5: Tokens are Returned to Application
    response_data = json.loads(post_request.text)

    #print(response_data)

    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]

    # Auth Step 6: Use the access token to access Spotify API
    authorization_header = {"Authorization": "Bearer {}".format(access_token)}

    # Get recently played
    user_profile_api_endpoint = "{}/me".format(SPOTIFY_API_URL)
    profile_response = requests.get(user_profile_api_endpoint, headers=authorization_header)
    profile_data = json.loads(profile_response.text)

    session['access_token'] = access_token
    session['profile_data'] = profile_data
    return redirect('/checklist') 

@app.route("/checklist", methods=["GET", "POST"])
def checklist():

    access_token = session['access_token']
    authorization_header = {"Authorization": "Bearer {}".format(access_token)}

    user_playlist_api_endpoint = "{}/me/player/recently-played?limit=50".format(SPOTIFY_API_URL)
    playlist_response = requests.get(user_playlist_api_endpoint, headers=authorization_header)
    playlist_data = json.loads(playlist_response.text)

    if request.method == "POST":
        result = list(dict(request.form).values())
        songs = result[2:len(result)-1]
        name = result[0]
        description = result[1]

        print(songs, name, description)

    return render_template("checklist.html", pd=playlist_data['items'])


if __name__ == "__main__":
    app.run(debug=True) 