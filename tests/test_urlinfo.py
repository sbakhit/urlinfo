import boto3
import pytest
import moto
from app import app

@pytest.fixture
def data_table():
    with moto.mock_dynamodb():
        client = boto3.client("dynamodb")
        client.create_table(
            AttributeDefinitions=[
                {"AttributeName": "url", "AttributeType": "S"},
            ],
            TableName='URLInfo',
            KeySchema=[
                {"AttributeName": "url", "KeyType": "HASH"},
            ],
            BillingMode="PAY_PER_REQUEST"
        )

        yield 'URLInfo'

@pytest.fixture
def data_table_with_transactions(data_table):
    """Creates transactions for a client with a total of 9"""

    table = boto3.resource("dynamodb").Table(data_table)

    data = [
        {"url": "goodurl.com", "is_safe": True},
        {"url": "badurl.com", "is_safe": False}
    ]

    for d in data:
        table.put_item(Item=d)

def test_root_endpoint(data_table):
    with app.test_client() as c:
        response = c.get('/')
        assert response.status_code == 200
        json_response = response.get_json()
        assert json_response.get('msg') == 'Specify API'

def test_urlinfo_root_endpoint(data_table):
    with app.test_client() as c:
        response = c.get('/urlinfo')
        assert response.status_code == 200
        json_response = response.get_json()
        assert json_response.get('msg') == 'Specify API Version'

def test_urlinfo_get_200_safe(data_table_with_transactions):
    with app.test_client() as c:
        test_url = 'goodurl.com'
        response = c.get('/urlinfo/1/{url}'.format(url=test_url))
        assert response.status_code == 200
        json_response = response.get_json()
        assert json_response.get('Item') == {'url': test_url, 'is_safe': True}

def test_urlinfo_get_200_unsafe(data_table_with_transactions):
    with app.test_client() as c:
        test_url = 'badurl.com'
        response = c.get('/urlinfo/1/{url}'.format(url=test_url))
        assert response.status_code == 200
        json_response = response.get_json()
        assert json_response.get('Item') == {'url': test_url, 'is_safe': False}

def test_urlinfo_get_404(data_table_with_transactions):
    with app.test_client() as c:
        test_url = 'testurl.com'
        response = c.get('/urlinfo/1/{url}'.format(url=test_url))
        assert response.status_code == 404
        json_response = response.get_json()
        assert json_response.get('msg') == 'Not Found'

def test_urlinfo_update_safe_200(data_table_with_transactions):
    with app.test_client() as c:
        test_url = 'testurl.com'
        response = c.put('/urlinfo/1/{url}/safe'.format(url=test_url))
        assert response.status_code == 200
        json_response = response.get_json()
        assert json_response.get('msg') == 'Updated successfully'

        response = c.get('/urlinfo/1/{url}'.format(url=test_url))
        assert response.status_code == 200
        json_response = response.get_json()
        assert json_response.get('Item') == {'url': test_url, 'is_safe': True}

def test_urlinfo_update_unsafe_200(data_table_with_transactions):
    with app.test_client() as c:
        test_url = 'testurl.com'
        response = c.put('/urlinfo/1/{url}/unsafe'.format(url=test_url))
        assert response.status_code == 200
        json_response = response.get_json()
        assert json_response.get('msg') == 'Updated successfully'

        response = c.get('/urlinfo/1/{url}'.format(url=test_url))
        assert response.status_code == 200
        json_response = response.get_json()
        assert json_response.get('Item') == {'url': test_url, 'is_safe': False}

def test_urlinfo_delete_200(data_table_with_transactions):
    with app.test_client() as c:
        test_url = 'testurl.com'
        response = c.delete('/urlinfo/1/{url}'.format(url=test_url))
        assert response.status_code == 200
        json_response = response.get_json()
        assert json_response.get('msg') == 'Deleted successfully'

        response = c.get('/urlinfo/1/{url}'.format(url=test_url))
        assert response.status_code == 404
        json_response = response.get_json()
        assert json_response.get('msg') == 'Not Found'

