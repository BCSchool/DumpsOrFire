import json
# import os

# from django.conf import settings
from django.templatetags.static import static


def assign_letter_grade(pop_rating=0):
    """
    Assigns letter grade based on 0-100 popularity rating from Spotify API
    """
    r = pop_rating

    if r > 90:
        return "A"
    elif r > 80:
        return "B"
    elif r > 70:
        return "C"
    elif r > 60:
        return "D"
    elif r > 50:
        return "F"
    elif r > 40:
        return "G"
    elif r > 30:
        return "H"
    else:
        return "Z"


def get_description(letter_rating, type="track"):
    """
    Gets description and image path from json file based on letter grade given by assign_letter_grade
    """
    # file_path = os.path.join(settings.STATIC_ROOT, "spotify", "descriptions.json")
    file_path = static("spotify/descriptions.json")

    json_data = open(file_path, "r")
    data = json.load(json_data)

    json_data.close()

    desc = data[letter_rating][type]
    img = data[letter_rating]["reaction"]

    return desc, img


def format_rating(generated_rating=0, type="track"):
    """
    Uses get_description with letter grade as input to return description and image path to view
    """
    return get_description(assign_letter_grade(generated_rating), type)
