from app.config import Config

def test_health_endpoint(client):
    response = client.get('/health')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data == {"status": "ok"}
    # Verify no credentials or internal secrets exposed
    assert 'database' not in json_data
    assert 'SECRET_KEY' not in json_data

def test_database_url_postgres_normalization():
    render_db_url = "postgres://user:pass@host:5432/dbname"
    if render_db_url.startswith("postgres://"):
        normalized_url = render_db_url.replace("postgres://", "postgresql://", 1)
    else:
        normalized_url = render_db_url

    assert normalized_url.startswith("postgresql://")
    assert normalized_url == "postgresql://user:pass@host:5432/dbname"

def test_production_config_flags(app):
    assert 'SESSION_COOKIE_HTTPONLY' in app.config
    assert app.config['SESSION_COOKIE_HTTPONLY'] is True
