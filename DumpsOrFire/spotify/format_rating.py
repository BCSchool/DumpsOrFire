import json
from django.core.files.storage import FileSystemStorage
from django.conf import settings

# import rating_reaction

def assign_letter_grade(pop_rating = 0):
    r = pop_rating

    if r > 90:
        return 'A'
    elif r > 80:
        return 'B'
    elif r > 70:
        return 'C'
    elif r > 60:
        return 'D'
    elif r > 50:
        return 'F'
    elif r > 40:
        return 'G'
    elif r > 30:
        return 'H'
    else:
        return 'Z'
    
def get_description(letter_rating, type = 'Track'):
    fs = FileSystemStorage(location=settings.STATIC_ROOT)
    file_path = fs.path('spotify/descriptions.json')

    json_data = open(file_path, 'r')
    data = json.load(json_data)

    json_data.close()

    desc = data[letter_rating][type]
    img = data[letter_rating]['Reaction']

    return desc, img

def format_rating(generated_rating = 0, type = 'Track'):
    return get_description(assign_letter_grade(generated_rating), type)
