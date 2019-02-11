import re
import json
import wptools
import wikipediaapi

BR_REGEX = re.compile('(<br ?/?>)?(and|with)? ?\[*([-\w()|.\' ]+(\w|\.))\]* ?(<br ?/?>)?')
COMMA_REGEX = re.compile(',?([-\w()|.\' ]+(\w|\.)),?')
PLAIN_UBL_REGEX = re.compile('[*|]+ ?\[*([-\w()|.\' ]+(\w|\.))\]*')
DOUBLE_BRACES_REGEX = re.compile('\[+([-\w()|.\' ]+)\]+')

TIME_REGEX = re.compile('(\d+) ?[hours]* ?(\d*) ?[minutes]*')
MYSTERY_REGEX = re.compile('[*\[]* ?([-\w| ]+\w)\]* ?(<br ?/?>)*,*/* ?')
FUZZY_LIST_REGEX = re.compile('[*|]* ?([\w(). ]+) ?')


def parse_plain_ubl_list(string_raw):
    """
    typically parse string like this:
        "{{Plainlist|\n* [[Abbi Jacobson]]\n* [[Dave Franco]]\n* Charlotte Carel\n* Madeline Carel\n* Dawan Owens\n* Jen Tullock\n* [[Maya Erskine]]\n* [[Tim Matheson]]\n* [[Jane Kaczmarek]]}}",
        "{{Unbulleted list|[[Rajinikanth]]|[[Akshay Kumar]]|[[Amy Jackson]]|[[Sudhanshu Pandey]]}}",
        "{{ubl|Johnny Knoxville|[[Chris Pontius]]}}"
        "{{Plainlist|\n* [[Michael Rainey Jr.]]}}"

    :param string_raw: string to parse
    :return: parsed list of names
    """
    list_raw = PLAIN_UBL_REGEX.findall(string_raw)
    return [i[0].strip() for i in list_raw]


def parse_br_list(string_raw):
    """
    typically parse string like this:
        "[[Behnaz Jafari]]<br />Jafar Panahi<br />Marziyeh Rezaei<br />Maedeh Erteghaei",
        "[[Marie B\u00e4umer]]<br>[[Birgit Minichmayr]]<br>[[Charly H\u00fcbner]]<br>[[Robert Gwisdek]]",
        "Arun Gowda,<br>[[Kavya Shetty]]",
        "[[Scott Adkins]]<br>[[Ray Stevenson]]<br>[[David Paymer]]<br>[[Ray Park]]<br>with [[Michael Jai White]]<br>and [[Ashley Greene]]",
        "[[Ravi Teja]]<br />[[Ileana D'Cruz]]",
        "{{Plainlist|\n* [[Ha Jung-woo]]\n* [[Ju Ji-hoon]]\n* [[Kim Hyang-gi]]\n* [[Ma Dong-seok]]\n* [[Kim Dong-wook]]}}",

    :param string_raw: string to parse
    :return: parsed list of names
    """
    list_raw = BR_REGEX.findall(string_raw)
    return [i[2].strip() for i in list_raw]


def parse_double_braces_list(string_raw):
    """
    typically parse stirng like this:
        "[[Tony Trov]] and [[Johnny Zito]]",

    :param string_raw: string to parse
    :return: parsed list of names
    """
    return DOUBLE_BRACES_REGEX.findall(string_raw)


def parse_comma_list(string_raw):
    """
    typically parse string like this:
        "Paris Hilton, Josh Ostrovsky, Kirill Bichutsky, Brittany Furlan, Hailey Baldwin, DJ Khaled, Emily Ratajkowski",

    :param string_raw: string to parse
    :return: parsed list of names
    """
    list_raw = COMMA_REGEX.findall(string_raw)
    return [i[0].strip() for i in list_raw]


def get_infobox(wikipage):
    """
    get infobox by using wptools
    :param wikipage: wikipage object
    :return: infobox dict
    """
    movie_name = wikipage.title
    if not movie_name.startswith('Category'):
        page = wptools.page(movie_name)
        page.get_parse()
        return page.data['infobox']


def get_title(wikipage):
    """
    get title of wiki page
    :param wikipage: wikipage object
    :return: name of page
    """
    return wikipage.title


def get_director(infobox):
    """
    parse string containing directors' name
    here are samples:
        "director": "[[Radha Mohan]]",
        "director": "[[Amr Gamal (director)|Amr Gamal]]",
        "director": "[[S. Shankar|Shankar]]",
        "director": "[[Hughes brothers|Albert Hughes]]",
        "director": "[[Tony Trov]] and [[Johnny Zito]]",

        "director": "{{Plainlist|\n* [[Hannah Marks]]\n* Joey Power}}",
        "director": "*Natasha Museveni Karugire\n*Sharpe Ssewali",

        "director": "Suzi Ewing",

    :param infobox: infobox dict
    :return: list of directors' name
    """
    try:
        director_raw = infobox.get('director')
        if '*' in director_raw:
            return parse_plain_ubl_list(director_raw)
        elif '[[' in director_raw:
            return parse_double_braces_list(director_raw)
        else:
            return [director_raw]
    except:
        return []


def get_starring(infobox):
    """
    parse string containing starring' name
    here are samples:
        "starring": "{{Plainlist|\n* [[Mehwish Hayat]]\n* [[Fahad Mustafa]]\n* [[Sarwat Gillani]]\n* [[Nimra Bucha]]\n* [[Behroze Sabzwari]]}}",
        "starring": "{{Plainlist|\n* [[Abbi Jacobson]]\n* [[Dave Franco]]\n* Charlotte Carel\n* Madeline Carel\n* Dawan Owens\n* Jen Tullock\n* [[Maya Erskine]]\n* [[Tim Matheson]]\n* [[Jane Kaczmarek]]}}",
        "starring": "{{Plainlist|\n|<!-- Order per the film's billing block -->\n|* Anum Zaidi\n* Natasha Humera Ejaz\n* Ali Noor\n* Azfar Jafri\n* Abdul Nabi Jamali\n* Arieb Azhar\n* Hareem Farooq\n* Ali Rehman Khan\n* Arshad Mehmood\n* Amjad Chaudary\n* Ahmed Ali}} * Anum Zaidi\n* Natasha Humera Ejaz\n* Ali Noor\n* Azfar Jafri\n* Abdul Nabi Jamali\n* Arieb Azhar\n* Hareem Farooq\n* Ali Rehman Khan\n* Arshad Mehmood\n* Amjad Chaudary\n* Ahmed Ali",
        "starring": "{{Plainlist|<!-- Order per billing block -->|\n* |<!--Please do not add a link here. It is an OVERLINK as Rudd is credited as a writer and linked above. Thank you!-->|Paul Rudd|<!--Please do not add a link here. It is an OVERLINK as Rudd is credited as a writer and linked above. Thank you!-->|\n* [[Evangeline Lilly]]\n* [[Michael Pe\u00f1a]]\n* [[Walton Goggins]]\n* [[Bobby Cannavale]]\n* [[Judy Greer]]\n* [[T.I.|Tip \"T.I.\" Harris]]\n* [[David Dastmalchian]]\n* [[Hannah John-Kamen]]\n* [[Abby Ryder Fortson]]\n* [[Randall Park]]\n* [[Michelle Pfeiffer]]\n* [[Laurence Fishburne]]\n* [[Michael Douglas]]}} * Paul Rudd * [[Evangeline Lilly]]\n* [[Michael Pe\u00f1a]]\n* [[Walton Goggins]]\n* [[Bobby Cannavale]]\n* [[Judy Greer]]\n* [[T.I.|Tip \"T.I.\" Harris]]\n* [[David Dastmalchian]]\n* [[Hannah John-Kamen]]\n* [[Abby Ryder Fortson]]\n* [[Randall Park]]\n* [[Michelle Pfeiffer]]\n* [[Laurence Fishburne]]\n* [[Michael Douglas]]",

        "starring": "{{Unbulleted list|[[Rajinikanth]]|[[Akshay Kumar]]|[[Amy Jackson]]|[[Sudhanshu Pandey]]}}",
        "starring": "{{ubl|Johnny Knoxville|[[Chris Pontius]]}}",
        "starring": "{{ubl|[[Jake Thomas]]|[[Chris Brochu]]|Michelle DeShon|Arienne Mandi|Zoe Corraface}}",

        "starring": "[[Behnaz Jafari]]<br />Jafar Panahi<br />Marziyeh Rezaei<br />Maedeh Erteghaei",
        "starring": "[[Marie B\u00e4umer]]<br>[[Birgit Minichmayr]]<br>[[Charly H\u00fcbner]]<br>[[Robert Gwisdek]]",
        "starring": "Arun Gowda,<br>[[Kavya Shetty]]",
        "starring": "Subash Chandra Bose<br>Dhaanya",
        "starring": "[[Kelly Reilly]]<br />[[Luke Evans (actor)|Luke Evans]]<br />Olivia Chenery",

        "starring": "Paris Hilton, Josh Ostrovsky, Kirill Bichutsky, Brittany Furlan, Hailey Baldwin, DJ Khaled, Emily Ratajkowski",

    :param infobox: infobox dict
    :return: list of starring' name
    """
    try:
        starring_raw = infobox.get('starring')
        if any(i in starring_raw for i in ('*', 'ubl|', 'list|')):
            return parse_plain_ubl_list(starring_raw)
        elif 'br' in starring_raw:
            return parse_br_list(starring_raw)
        elif ',' in starring_raw:
            return parse_comma_list(starring_raw)
        elif '[[' in starring_raw:
            return parse_double_braces_list(starring_raw)
        else:
            return [starring_raw]
    except:
        return []


def get_runtime(infobox):
    """
    parse string containing runtime, return time in minutes, only retain first result
    here are samples:
        "runtime": "147 minutes",
        "runtime": "102 min",
        "runtime": "2h 35min",
        "runtime": "125 minutes (Tamil)<br />145 minutes (Malayalam)",
        "runtime": "29 - 30 mins",
        "runtime": "2 hours 19 minutes",

    :param infobox: infobox dict
    :return: string of runtime
    """
    try:
        time_raw = infobox.get('runtime')
        time_list_raw = TIME_REGEX.findall(time_raw)[0]
        if time_list_raw[1] == '':
            if int(time_list_raw[0]) > 2:
                return int(time_list_raw[0])
            else:
                return int(time_list_raw[0]) * 60
        elif time_list_raw[1] != '':
            return int(time_list_raw[0]) * 60 + int(time_list_raw[1])
        else:
            return ''
    except:
        return ''


def get_country(infobox):
    """
    parse string containing country
    here are samples:
        "country": "Germany<br>Austria<br>France",
        "country": "[[India]]<br>[[Canada]] <br> [[Australia]]",
        "country": "[[Indonesia]]",
        "country": "Australia/[[Sri Lanka]]",

        "country": "{{plainlist|\n*Sudan\n*South African\n*Qatar\n*Germany}}",
        "country": "{{ubl|United Kingdom|United States|ref|{{cite news|url=https://variety.com/2018/film/reviews/american-animals-review-1202669037/|last=Lodge|first=Guy|publisher=[[Penske Business Media]]|title=Film Review: 'American Animals'|date=January 19, 2018|accessdate=August 18, 2018 |work=[[Variety (magazine)|Variety]]}}|</ref>}}",
        "country": "{{hlist|Argentina|Mexico}}",
        "country": "{{US}}",

        "country": "Pakistan",

    :param infobox: infobox dict
    :return: list of countries' name
    """
    try:
        country_raw = infobox.get('country')
        if '{' not in country_raw:
            country_list_raw = MYSTERY_REGEX.findall(country_raw)
            return [i[0].strip() for i in country_list_raw]
        elif '{' in country_raw:
            country_list_raw = FUZZY_LIST_REGEX.findall(country_raw.split('ref')[0])
            if any(i in country_raw for i in ('ubl', 'list')):
                return [i.strip() for i in country_list_raw[1:]]
            else:
                return [country_list_raw]
        else:
            return [country_raw]
    except:
        return []


def get_language(infobox):
    """
    parse string containing country
    here are samples:
        "language": "Tamil",
        "language": "[[Kannada]]"
        "language": "[[Odia language|Odia]]"
        "language": "Hindi <br> English"
        "language": "English, Swahili"
        "language": "English / Sinhala"
        "language": "[[Fictional language]]",
        "language": "{{Plainlist|\n* English\n* Arabic\n* Hebrew}}",
        "language": "{{ubl|English|French}}",

    :param infobox: infobox dict
    :return: list of language list
    """
    try:
        language_raw = infobox.get('language')
        if any(i in language_raw for i in ('*', 'ubl|', 'list|')):
            return parse_plain_ubl_list(language_raw)
        else:
            language_list_raw = MYSTERY_REGEX.findall(language_raw)
            return [i[0].strip() for i in language_list_raw]
    except:
        return []


def get_time():
    """
    TODO
    """
    pass


def get_location():
    """
    TODO
    """
    pass


def get_text(infobox):
    """
    return string of all text
    :param infobox: infobox dict from processed json file
    :return: text field of wiki page
    """
    try:
        return infobox.get('text')
    except:
        return ''


def parse_categories(wikipage):
    """
    parse and return  list of categories

    :param wikipage: wikipage object
    :return: categories of wiki page
    """
    try:
        return [c[9:] for c in wikipage.categories]
    except:
        return ''


def get_categories(infobox):
    """
    return list of categories

    {'Category:2010s Tamil-language films': Category:2010s Tamil-language films (id: ??, ns: 14),
    'Category:2010s action films': Category:2010s action films (id: ??, ns: 14),
    'Category:2010s science fiction action films': Category:2010s science fiction action films (id: ??, ns: 14)}

    :param infobox: infobox dict from processed json file
    :return: categories of wiki page
    """
    try:
        return infobox.get('category')
    except:
        return []


def get_data_dict(infobox, wikipage):
    """
    return formed data as dict

    :param infobox: infobox dict
    :param wikipage: wikipage object
    :return: formed data dict
    """
    return {'Title': get_title(wikipage),
            'Director': get_director(infobox),
            'Starring': get_starring(infobox),
            'Running time': get_runtime(infobox),
            'Country': get_country(infobox),
            'Language': get_language(infobox),
            'Time': '',
            'Location': '',
            'Categories': get_categories(infobox),
            'Text': get_text(infobox)}


def running_log(log):
    """
    print and write running log

    :param log: string to log
    """
    print(log)
    with open('running_log.txt', 'a') as f:
        f.write(log + '\n')


def collect_raw_data():
    """
    collect infobox and categories and text of all pages

    :return: json file containing all info
    """
    try:
        # get all pages
        wiki = wikipediaapi.Wikipedia('en')
        cat = wiki.page("Category:2018 films")
        cat_pages = [wiki.page(p) for p in cat.categorymembers]

        index = 1
        json_dict = {}
        for wikipage in cat_pages:
            infobox = get_infobox(wikipage) or {}
            infobox['title'] = wikipage.title
            infobox['text'] = wikipage.text
            infobox['category'] = parse_categories(wikipage)

            json_dict[index] = infobox
            index += 1
    except:
        pass
    finally:
        with open('raw_data_2.json', 'w') as output:
            json.dump(json_dict, output)
