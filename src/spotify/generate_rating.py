import base64
import json

from django.conf import settings
from requests import get, post
from requests.exceptions import RequestException, Timeout

client_id = settings.SOCIAL_AUTH_SPOTIFY_ID
client_secret = settings.SOCIAL_AUTH_SPOTIFY_SECRET


def get_token():
    """Get Spotify token to access artist and track info"""

    if settings.DEBUG:
        print("in get_token")

    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    if settings.DEBUG:
        print(f"client id: {client_id}")
        print(f"client secret: {client_secret}")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {"grant_type": "client_credentials"}
    try:
        if settings.DEBUG:
            print("attempting post request...")

        result = post(url, headers=headers, data=data, timeout=10)

    except Timeout:
        print("Request timed out after 10 seconds")
        raise
    except RequestException as e:
        print(f"Request failed: {str(e)}")
        raise

    if settings.DEBUG:
        print("Post request successfull")

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

    if settings.DEBUG:
        print(f"Recieved token: {token}")

    # Here we either use provided id or get one from the search
    if content_name != "" and input_id == "":
        result = user_search(token, content_name, search_type=content_type)
        if result is None:
            return None
        id = result["id"]
    else:
        id = input_id

    if settings.DEBUG:
        print(f"Recieved id from user_search: {id}")

    # Search for content and return items associated with content
    url = f"https://api.spotify.com/v1/{content_type}s"
    headers = get_auth_header(token)
    query = f"/{id}"

    if settings.DEBUG:
        print(f"Auth headers recieved: {headers}")

    query_url = url + query

    try:
        result = get(query_url, headers=headers, timeout=10)

        if result.status_code != 200:
            print(f"Error response from Spotify: {result.text}")
            result.raise_for_status()

    except Timeout:
        print("Request timed out after 10 seconds")
        raise
    except RequestException as e:
        print(f"Request failed: {str(e)}")
        raise

    # result = get(query_url, headers=headers)

    try:
        json_result = json.loads(result.content)
    
    except Exception as e:
        print(f"JSON error: {str(e)}")
    
    # Get popularity of content (using avg function if playlist)
    if content_type == "playlist":
        popularity = get_avg_popularity(json_result)
    else:
        popularity = json_result["popularity"]

    if settings.DEBUG:
        print(f"Popularity found: {popularity}")

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


def get_avg_popularity(json_result):
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

    if settings.DEBUG:
        print(f"query url: {query_url}")
        print("Attempting GET request...")

    try:
        result = get(query_url, headers=headers, timeout=10)

        if result.status_code != 200:
            print(f"Error response from Spotify: {result.text}")
            result.raise_for_status()

    except Timeout:
        print("Request timed out after 10 seconds")
        raise
    except RequestException as e:
        print(f"Request failed: {str(e)}")
        raise

    if settings.DEBUG:
        print(f"Successfully got response: {result}")

    try:
        json_data = json.loads(result.content)
        # json_result = json.loads(result.content)[f"{search_type}s"]["items"]
        if settings.DEBUG:
            print("Successfully parsed JSON")

        json_result = json_data[f"{search_type}s"]["items"]

        if settings.DEBUG:
            print(f"Found {len(json_result)} items")

    except (KeyError, json.JSONDecodeError) as e:
        print(f"Error parsing response: {str(e)}")
        print(f"Raw response: {result.text[:200]}...")
        raise

    if len(json_result) == 0:
        print(f"No {search_type} with this name exists...")
        return None

    return json_result[0]
