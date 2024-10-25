from django.http import HttpResponse
from django.shortcuts import render
from django.templatetags.static import static

from . import format_rating as fr
from . import generate_rating as gr
from . import url_parser as up

# Create your views here.


def favicon(request):
    return HttpResponse(status=204)


def index(request):
    """
    This function is called when the user first accesses the website.
    It loads the index page.
    """
    return render(request, "spotify/index.html")


def rate(request):
    """
    This function is called when the user submits a search query.
    It is responsible for getting the user input and calling the functions that will get the rating and description.
    """
    context = {}
    if request.method == "POST":
        # Get user input and change search type text in search box
        user_input = request.POST.get("user_input")
        search_type = request.POST.get("search_type")

        if len(user_input) > 50 and search_type != "link":
            context["error"] = (
                "Search query too long, please try again with a shorter query."
            )
            return render(request, "spotify/rate.html", context)

        context["search_type"] = search_type
        id = ""

        # if user provides a link we can deconstruct the URL and use the id to search the API.
        # Otherwise we use the search term provided and let the function get the associated id from the API.
        if search_type == "link":
            if not up.validate_url(user_input):
                context["error"] = (
                    "Invalid Spotify link, please try again with a valid link."
                )
                return render(request, "spotify/rate.html", context)

            search_type = up.get_url_type(user_input)
            id = up.get_url_id(user_input)  # is empty string if not url

        # get rating from api and description from json file
        result = None
        try:
            result = gr.get_popularity(
                content_type=search_type, content_name=user_input, input_id=id
            )

        except Exception as e:
            print(str(e))
            context["error"] = (
                "Error fetching data from Spotify API, please try a different track or again later."
            )
            return render(request, "spotify/rate.html", context)

        if result is not None:
            popularity, name, image = result

            """get rating from api and description from json file"""
            context["rating"] = popularity

            desc, img = fr.format_rating(popularity, type=search_type)

            context["description"] = desc
            # context["reaction"] = f"static/spotify/rating_reaction/{img}"
            context["reaction"] = static(f'spotify/rating_reaction{img}')

            context["image"] = image
            context["name"] = name

    return render(request, "spotify/rate.html", context)
