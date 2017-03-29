from spacy_api import Client


def test_single():
    spacy_client = Client()
    doc = spacy_client.single("How are you")
    assert doc


def test_bulk():
    spacy_client = Client()
    docs = spacy_client.bulk(["How are you"] * 1001)
    assert docs
