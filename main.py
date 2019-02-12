"""
Assignment 2: Building a Corpus
Name: Chenfeng Fan (fanc@brandeis.edu)
"""

import json
import wptools
import wikipediaapi
from helper import *


def main(output_name='output/2018_movies.json'):
    # read pre collected raw data json file, which contains all infobox data, page title, categories, and text
    with open('input/raw_data.json') as f:
        json_data_raw = json.load(f)

    json_dict = {}
    # iterate through all infoboxes
    for index in json_data_raw:
        infobox = json_data_raw[index]
        data_dict = get_data_dict(infobox)
        json_dict[index] = data_dict
        # if index == '100':
        #     break

    # write output json file
    with open(output_name, 'w') as output:
        json.dump(json_dict, output)


if __name__ == '__main__':
    # collect_raw_data()  # run this line if want to collect raw data again, it will take a long time.
    main('output/2018_movies_2.json')
