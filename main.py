import json
from lips.api_client import get_mentors_or_congratulations


def fetch_mentors(url):
    mentors_json = get_mentors_or_congratulations(url, 'mentors')
    mentors = json.loads(mentors_json)
    return mentors


def fetch_congratulations(url):
    congratulations_json = get_mentors_or_congratulations(
        url, 'congratulations')
    congratulations = json.loads(congratulations_json)
    return congratulations


def fetch_ascii_art(url):
    ascii_art_json = get_mentors_or_congratulations(url, 'asciiart')
    ascii_art = json.loads(ascii_art_json)
    return ascii_art


def main():
    url_mentors = 'http://127.0.0.1:8000/mentors'
    url_congratulations = 'http://127.0.0.1:8000/congratulations'
    url_ascii = 'http://127.0.0.1:8000/asciiart'

    mentors = fetch_mentors(url_mentors)
    congratulations = fetch_congratulations(url_congratulations)
    ascii_art = fetch_ascii_art(url_ascii)

    print(mentors)
    print('')
    print(congratulations)
    print('~~~Example~~~')
    print(mentors['mentors'][0]['last_name'])
    print(mentors['mentors'][0]['first_name'])
    print(mentors['mentors'][0]['tg_id'])
    print(congratulations['congratulations'][0])
    for line in ascii_art['ASCIIART']:
        print(line)


if __name__ == '__main__':
    main()