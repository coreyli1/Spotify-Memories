from flask import Flask, render_template, redirect, request, session, url_for
from urllib.parse import quote
import requests
import json

app = Flask(__name__)


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
    print(auth_url)
    return redirect(auth_url)

@app.route("/callback/q", methods = ['GET', 'POST'])
def callback():
    # Auth Step 4: Requests refresh and access tokens

    print(request.args)

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
    user_profile_api_endpoint = "{}/me/player/recently-played?limit=50".format(SPOTIFY_API_URL)
    profile_response = requests.get(user_profile_api_endpoint, headers=authorization_header)
    profile_data = json.loads(profile_response.text)

    # print(profile_data['items'])

    #return redirect('/checklist') 
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        return redirect(url_for('confirmation', name=name, description=description))
    
    return render_template("checklist.html", pd=profile_data['items'])


@app.route("/confirmation")
def confirmation():
    user_profile_api_endpoint = "{}/me".format(SPOTIFY_API_URL)
    user_profile_response = requests.get(user_profile_api_endpoint, headers=authorization_header)
    user_profile_data = json.loads(user_profile_response.text)
    user_id = user_profile_data['id']

    ##POST request to make a private playlist
    playslist_api_endpoint = "{}/users/{user_id}/playlists".format(SPOTIFY_API_URL)
    request_body = json.dumps({
        "name": name,
        "description": description,
        "public": False
    })

    ##POST reuest to push songs to the playlist
    response = requests.post(url = playslist_api_endpoint, data = request_body, headers={"Content-Type":"application/json", authorization_header})
    playlist_id = response.json()['id']
    add_tracks_api_endpoint = "{}/playlists/{playlist_id}/tracks".format(SPOTIFY_API_URL)
    request_body = json.dumps({
            "uris" : uris //make sure to pull uris from checklist
            })
    response = requests.post(url = endpoint_url, data = request_body, headers={"Content-Type":"application/json", authorization_header})


    return render_template("confirmation.html", name=name, playlist_id=playlist_id)

if __name__ == "__main__":
    app.run(debug=True) 