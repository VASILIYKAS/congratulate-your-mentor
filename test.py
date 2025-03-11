import httpx
import pytest


def test_empty_json():
    response = httpx.get('http://127.0.0.1:8000/empty')
    assert response.status_code == 200
    assert response.json() == {"mentors": []}


def test_invalid_json():
    response = httpx.get('http://127.0.0.1:8000/invalid')
    assert response.status_code == 200
    with pytest.raises(ValueError):
        response.json()


def test_missing_fields():
    response = httpx.get('http://127.0.0.1:8000/missing_fields')
    assert response.status_code == 200
    data = response.json()

    for mentor in data['mentors']:
        assert 'last_name' in mentor
        assert 'first_name' in mentor
        assert 'tg_id' in mentor
        assert 'user_name' in mentor


def test_wrong_types():
    response = httpx.get('http://127.0.0.1:8000/wrong_types')
    assert response.status_code == 200
    data = response.json()

    for mentor in data['mentors']:
        assert isinstance(mentor['last_name'], str)
        assert isinstance(mentor['first_name'], str)
        assert isinstance(mentor['tg_id'], int)
        assert isinstance(mentor['user_name'], str)


def test_extra_data():
    response = httpx.get('http://127.0.0.1:8000/extra_data')
    assert response.status_code == 200
    data = response.json()

    assert 'mentors' in data
    assert isinstance(data['mentors'], list)


def test_404_error():
    response = httpx.get('http://127.0.0.1:8000/not_found')
    assert response.status_code == 404


def test_400_error():
    response = httpx.get('http://127.0.0.1:8000/bad_request')
    assert response.status_code == 400


def test_500_error():
    response = httpx.get('http://127.0.0.1:8000/internal_server_error')
    assert response.status_code == 500