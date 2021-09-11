from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_news_list():
    """
        Test if the news list api is returning the data with the correct format.
    """
    response = client.get("/news")
    assert response.status_code == 200
    assert isinstance(response.json(), list) is True
    assert len(response.json()) != 0
    assert list(response.json()[0].keys()) == ["headline", "link", "source"]


def test_news_search():
    """
        Test if the news search api is returning the data with the correct format.
    """
    response = client.get("/news?query=bitcoin")
    assert response.status_code == 200
    assert isinstance(response.json(), list) is True
    assert len(response.json()) != 0
    assert list(response.json()[0].keys()) == ["headline", "link", "source"]
