from types import GeneratorType
import cachetools.func

nlp_objects = {}

DEFAULT_ATTRIBUTES = ("text", "lemma_", "pos_", "tag_", "vector")


def get_nlp(model="en", embeddings_path=None):
    import spacy
    if embeddings_path not in nlp_objects:
        if embeddings_path is None:
            nlp_ = spacy.load(model)
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
    elif hasattr(value, "__iter__"):
        if x == "children":
            return [x.i for x in value]
        return list(value)
    elif isinstance(value, list):
        return value
    else:
        # vectors
        return [float(x) for x in value]


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
    print("a1", attributes)
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
