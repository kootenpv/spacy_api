from spacy_api import Connector


def test_single():
    spacy_client = Connector()
    doc = spacy_client.single("How are you")
    assert doc


def test_bulk():
    spacy_client = Connector()
    docs = spacy_client.bulk(["How are you"] * 1001)
    assert docs
