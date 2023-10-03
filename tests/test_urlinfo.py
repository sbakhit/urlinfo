from app import app

def test_root_endpoint():
    with app.test_client() as c:
        response = c.get('/')
        assert response.status_code == 200
        json_response = response.get_json()
        assert json_response == {'msg': 'Specify API'}

def test_urlinfo_root_endpoint():
    with app.test_client() as c:
        response = c.get('/urlinfo')
        assert response.status_code == 200
        json_response = response.get_json()
        assert json_response == {'msg': 'Specify API Version'}

def test_urlinfo_get_200_safe():
    with app.test_client() as c:
        response = c.get('/urlinfo/1/goodurl.com')
        assert response.status_code == 200
        json_response = response.get_json()
        assert json_response == {'Item': {'url': 'goodurl.com', 'is_safe': True}}

def test_urlinfo_get_200_unsafe():
    with app.test_client() as c:
        response = c.get('/urlinfo/1/badurl.com')
        assert response.status_code == 200
        json_response = response.get_json()
        assert json_response == {'Item': {'url': 'badurl.com', 'is_safe': False}}

def test_urlinfo_get_404():
    with app.test_client() as c:
        response = c.get('/urlinfo/1/notfound.com')
        assert response.status_code == 404
        json_response = response.get_json()
        assert json_response == {'msg': 'Not Found'}

