import tqdm
import math
import numpy as np
import functools
import requests


class SpacyClientToken():

    def __init__(self, **kwargs):
        self.attributes = kwargs
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def _vector(self):
        if isinstance(self.vector, list):
            self.vector = np.array(self.vector)
        return self.vector

    def __repr__(self):
        if "text" in self.attributes:
            return self.text
        else:
            return self.lemma_


class SpacyClientSentence(list):

    def __init__(self, tokens):
        self.tokens = [SpacyClientToken(**token) for token in tokens]
        super(SpacyClientSentence, self).__init__(self.tokens)
        self._vector = None

    @property
    def vector(self):
        if self._vector is None:
            self._vector = np.mean([x._vector for x in self.tokens], axis=0)
        return self._vector

    def __getitem__(self, i):
        return self.tokens[0]


class SpacyClientDocument(list):

    def __init__(self, document):
        self.sents = [SpacyClientSentence(x) for x in document]
        super(SpacyClientDocument, self).__init__(self.sents)
        self._vector = None

    @property
    def vector(self):
        if self._vector is None:
            self._vector = np.mean([x.vector for x in self.sents], axis=0)
        return self._vector

    def __getitem__(self, i):
        return self.sents[0]

    def __iter__(self):
        for sentence in self.sents:
            for token in sentence:
                yield token


class Connector():

    def __init__(self, host="http://localhost", port=9033):
        self.host = host
        self.port = port
        self.url = "{}:{}/".format(host, port)

    def _post(self, path, **kwargs):
        resp = requests.post(self.url + path, json=kwargs)
        return resp.json()

    @functools.lru_cache(maxsize=3000000)
    def single(self, document, model="en", embeddings_path=None, attributes=None):
        sentences = self._post("single", document=document, model=model,
                               embeddings_path=embeddings_path, attributes=attributes)["sentences"]
        return SpacyClientDocument(sentences)

    def _bulk(self, documents, model, embeddings_path, attributes):
        return self._post("bulk", documents=documents, model=model,
                          embeddings_path=embeddings_path, attributes=attributes)

    def bulk(self, documents, model="en", batch_size=1000, embeddings_path=None, attributes=None):
        parsed_documents = []
        if len(documents) > batch_size:
            batches = int(math.ceil(len(documents) / batch_size))
            print("Batching {} requests with batch_size {}".format(batches, batch_size))
            for b in tqdm.tqdm(range(batches)):
                docs = documents[b * batch_size:(b + 1) * batch_size]
                res = self._bulk(docs, model, embeddings_path, attributes)["documents"]
                parsed_documents.extend(res)
        else:
            parsed_documents = [self.single(d, model, embeddings_path, attributes)
                                for d in documents]
        return parsed_documents
