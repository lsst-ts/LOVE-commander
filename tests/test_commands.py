def test_hello_world(client):
    """Start with a blank database."""

    rv = client.get('/')
    assert rv.data.decode('utf-8') == 'Hello, World!\n'