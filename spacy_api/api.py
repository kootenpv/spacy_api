import math
import tqdm
import functools
import spacy

nlp_objects = {}

DEFAULT_ATTRIBUTES = ("text", "lemma_", "pos_", "tag_", "vector")


def get_nlp(model="en", embeddings_path=None):
    if embeddings_path not in nlp_objects:
        if embeddings_path is None:
            nlp_ = spacy.load(model)
        else:
            nlp_ = spacy.load(model, vectors=embeddings_path)
        nlp_objects[embeddings_path] = nlp_
    return nlp_objects[embeddings_path]


def json_safety(token, x):
    value = getattr(token, x)
    if isinstance(value, (str, int)):
        return value
    else:
        return [float(x) for x in value]


@functools.lru_cache(maxsize=3000000)
def single(document, model="en", embeddings_path=None, attributes=None):
    if attributes is None:
        attributes = DEFAULT_ATTRIBUTES
    nlp_ = get_nlp(model, embeddings_path)
    sentences = []
    for sent in nlp_(document).sents:
        sentence = [{x: json_safety(token, x) for x in attributes}
                    for token in sent]
        sentences.append(sentence)
    return {"sentences": sentences}


@functools.lru_cache(maxsize=10000)
def _bulk(documents, model, batch_size, embeddings_path, attributes):
    if attributes is None:
        attributes = DEFAULT_ATTRIBUTES
    if len(documents) > batch_size:
        parsed_documents = []
        batches = int(math.ceil(len(documents) / batch_size))
        for b in tqdm.tqdm(range(batches)):
            docs = documents[b * batch_size:(b + 1) * batch_size]
            res = [single(d, model, embeddings_path, attributes) for d in docs]
            parsed_documents.extend(res)
    else:
        parsed_documents = [single(d, model, embeddings_path, attributes) for d in documents]
    return {"documents": parsed_documents}


def bulk(documents, model="en", batch_size=1000, embeddings_path=None, attributes=None):
    documents = tuple(documents)
    return _bulk(documents, model, batch_size, embeddings_path, attributes)
