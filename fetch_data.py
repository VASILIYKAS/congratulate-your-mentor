from libs.api_client import get_mentors_or_congratulations


def fetch_mentors():
    url = 'https://my-json-server.typicode.com/devmanorg/congrats-mentor'
    endpoint = '/mentors'
    mentors = get_mentors_or_congratulations(url, endpoint)
    return mentors


def fetch_postcards():
    url = 'https://my-json-server.typicode.com/devmanorg/congrats-mentor'
    endpoint = '/postcards'
    congratulations = get_mentors_or_congratulations(
        url, endpoint)
    return congratulations


def fetch_ascii_art(url):
    ascii_art = get_mentors_or_congratulations(url, 'asciiart')
    return ascii_art
