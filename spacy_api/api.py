from types import GeneratorType
import cachetools.func
import os

nlp_objects = {}

DEFAULT_ATTRIBUTES = ("text", "lemma_", "pos_", "tag_", "vector")


def get_nlp(model="en", embeddings_path=None):
    import spacy
    if embeddings_path not in nlp_objects:
        if embeddings_path is None:
            nlp_ = spacy.load(model)
        else:
            if embeddings_path.endswith(".bin"):
                nlp_ = spacy.load(model, vectors=False)
                nlp_.vocab.load_vectors_from_bin_loc(embeddings_path)
            elif os.path.isdir(embeddings_path):
                from spacy.vectors import Vectors
                vectors = Vectors()
                vectors = vectors.from_disk(embeddings_path)
                nlp_ = spacy.load(model, vectors=False)
                nlp_.vocab.vectors = vectors
            else:
                nlp_ = spacy.load(model, vectors=embeddings_path)
        nlp_objects[embeddings_path] = nlp_
    return nlp_objects[embeddings_path]


def json_safety(token, x):
    try:
        value = getattr(token, x)
    except AttributeError:
        print(x, "not found on spacy object")
        value = "ERROR"
    if isinstance(value, (str, int, bool)):
        return value
    elif x == "vector":
        return [float(x) for x in value]
    elif hasattr(value, "__iter__"):
        if x == "children":
            return [x.i for x in value]
        return list(value)
    elif isinstance(value, list):
        return value
    else:
        return value


def convert_attr(attributes):
    if attributes is None:
        attributes = DEFAULT_ATTRIBUTES
    elif isinstance(attributes, str):
        attributes = tuple(attributes.replace(" ", "").split(","))
    return attributes


def add_root_attribute(tokenized_sentence, sent):
    root_index = sent.root.i
    for token in tokenized_sentence:
        token["root"] = root_index


@cachetools.func.lru_cache(maxsize=3000000)
def single(document, model="en", embeddings_path=None, attributes=None, local=False):
    attributes = convert_attr(attributes)
    needs_root = "root" in attributes
    nlp_ = get_nlp(model, embeddings_path)
    if local:
        sentences = nlp_(document)
    else:
        sentences = []
        for sent in nlp_(document).sents:
            tokenized_sentence = [{x: json_safety(token, x) for x in attributes}
                                  for token in sent]
            if needs_root:
                add_root_attribute(tokenized_sentence, sent)
            sentences.append(tokenized_sentence)
    return sentences


def bulk(documents, model="en", embeddings_path=None, attributes=None, local=False):
    attributes = convert_attr(attributes)
    parsed_documents = [single(d, model, embeddings_path, attributes, local)
                        for d in documents]
    return parsed_documents


@cachetools.func.lru_cache(maxsize=3000000)
def most_similar(word, n, model, embeddings_path):
    nlp_ = get_nlp(model, embeddings_path)
    word = nlp_(word)[0]
    queries = [w for w in word.vocab if w.is_lower == word.is_lower and w.prob >= -15]
    by_similarity = sorted(queries, key=word.similarity, reverse=True)
    return [x.orth_ for x in by_similarity[:n]]
