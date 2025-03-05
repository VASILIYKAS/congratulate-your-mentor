from libs.api_client import get_mentors_or_congratulations


def fetch_mentors():
    url = 'http://127.0.0.1:8000/mentors'
    mentors = get_mentors_or_congratulations(url, 'mentors')
    return mentors


def fetch_congratulations():
    url = 'http://127.0.0.1:8000/congratulations'
    congratulations = get_mentors_or_congratulations(
        url, 'congratulations')
    return congratulations


def fetch_ascii_art(url):
    ascii_art = get_mentors_or_congratulations(url, 'asciiart')
    return ascii_art


def main():
    # url_ascii = 'http://127.0.0.1:8000/asciiart'

    mentors = fetch_mentors()
    congratulations = fetch_congratulations()
    # ascii_art = fetch_ascii_art(url_ascii)

    print(mentors)
    print('')
    print(congratulations)
    print('~~~Example~~~')
    print(mentors['mentors'][0]['tg_id'])
    print(congratulations['congratulations'][0])
    # for line in ascii_art['ASCIIART']:
    #     print(line)


if __name__ == '__main__':
    main()