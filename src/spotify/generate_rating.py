import base64
import json

from django.conf import settings
from requests import get, post

client_id = settings.SOCIAL_AUTH_SPOTIFY_ID
client_secret = settings.SOCIAL_AUTH_SPOTIFY_SECRET


def get_token():
    """Get Spotify token to access artist and track info"""
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token


def get_auth_header(token):
    return {"Authorization": "Bearer " + token}


def get_popularity(content_type="track", content_name="", input_id=""):
    """
    Inputs: content_type (track, artist, or playlist), content_name (name of track, artist, or playlist), input_id (id of track, artist, or playlist from URL)
    Outputs: popularity rating, name of content, image of content

    If input_id is provided it means that the user searched with a link and the id is used to perform the search.
    Otherwise, the user searched with a track/album/playlist name and the name is used to perform the search.
    """
    if content_name == "" and input_id == "":
        return None

    token = get_token()

    # Here we either use provided id or get one from the search
    if content_name != "" and input_id == "":
        result = user_search(token, content_name, search_type=content_type)
        if result is None:
            return None
        id = result["id"]
    else:
        id = input_id

    # Search for content and return items associated with content
    url = f"https://api.spotify.com/v1/{content_type}s"
    headers = get_auth_header(token)
    query = f"/{id}"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)

    # Get popularity of content (using avg function if playlist)
    if content_type == "playlist":
        popularity = get_avg_popularity(result, json_result)
    else:
        popularity = json_result["popularity"]

    # Get name of content
    name = json_result["name"]
    if content_type != "playlist":
        name = name + " - " + json_result["artists"][0]["name"]

    # Get image of content
    if content_type == "track":
        image = json_result["album"]["images"][0]["url"]
    else:
        image = json_result["images"][0]["url"]

    return popularity, name, image


def get_avg_popularity(result, json_result):
    """
    Get average popularity of tracks in a playlist
    """
    sum = 0
    num_tracks = 0

    for track in json_result["tracks"]["items"]:
        result = track["track"]
        sum += result["popularity"]
        num_tracks += 1

    return sum // num_tracks


def user_search(token, track_name, search_type="track"):
    """
    Search for a track and return items associated with track using spotify API
    """
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={track_name}&type={search_type}&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)[f"{search_type}s"]["items"]

    if len(json_result) == 0:
        print(f"No {search_type} with this name exists...")
        return None

    return json_result[0]
