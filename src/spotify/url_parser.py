from urllib.parse import urlparse


def get_url_id(url: str) -> str:
    """uses urllib.parse.urlparse to extract the playlist id from a spotify playlist url"""
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.split("/")
    return path_parts[2][:22]  # id seems to always be 22 characters long


def get_url_type(url: str) -> str:
    """uses urllib.parse.urlparse to extract the content type from a spotify playlist url"""
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.split("/")
    return path_parts[1]


def validate_url(url: str) -> bool:
    """checks if the url is a valid spotify playlist url"""
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.split("/")
    if len(path_parts) != 3:
        return False
    if path_parts[1] not in ["track", "album", "playlist"]:
        return False
    if not path_parts[2][:22].isalnum():
        return False
    if parsed_url.netloc != "open.spotify.com":
        return False
    return True
