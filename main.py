import wikipediaapi
import wptools
import json
from helper import *


# collect_raw_data()

wiki = wikipediaapi.Wikipedia('en')
cat = wiki.page("Category:2018 films")
cat_pages = [wiki.page(p) for p in cat.categorymembers]

with open('raw_data.json') as f:
    json_data_raw = json.load(f)

index = 1
json_dict = {}
for wikipage in cat_pages:
    infobox = json_data_raw[str(index)]
    data_dict = get_data_dict(infobox, wikipage)
    json_dict[index] = data_dict

    index += 1
    # if index == 201:
    #     break
with open('output/2018_movies.json', 'w') as output:
    json.dump(json_dict, output)
