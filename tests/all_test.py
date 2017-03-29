from spacy_api import Client


def test_single():
    spacy_client = Client()
    doc = spacy_client.single("How are you")
    assert doc


def test_bulk():
    spacy_client = Client()
    docs = spacy_client.bulk(["How are you"] * 1001)
    assert docs


def test_string():
    spacy_client = Client()
    first_word = "How "
    sentence_text = "How are you. "
    doc_text = "How are you. How are you"
    doc = spacy_client.single(doc_text, attributes="string")
    assert doc.string == doc_text
    assert doc.sents[0].string == sentence_text
    assert doc[0].string == first_word
