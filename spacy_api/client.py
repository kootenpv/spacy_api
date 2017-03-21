import tqdm
import cachetools
import math
import numpy as np
from mprpc import RPCClient


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
        self._iter = []
        super(SpacyClientDocument, self).__init__(self.sents)
        self._vector = None

    @property
    def vector(self):
        if self._vector is None:
            self._vector = np.mean([x.vector for x in self.sents], axis=0)
        return self._vector

    def __getitem__(self, i):
        if not self._iter:
            for sentence in self.sents:
                for token in sentence:
                    self._iter.append(token)
        return self._iter[i]

    def __iter__(self):
        for sentence in self.sents:
            for token in sentence:
                yield token


class Connector():

    def __init__(self, host="127.0.0.1", port=9033, verbose=False):
        self.host = host
        self.port = port
        self.rpc = RPCClient(host, port)
        self.verbose = verbose

    def _call(self, path, *args):
        return self.rpc.call(path, *args)

    @cachetools.cached(cachetools.LRUCache(maxsize=3000000))
    def single(self, document, model="en", embeddings_path=None, attributes=None):
        sentences = self._call("single", document, model, embeddings_path, attributes)
        return SpacyClientDocument(sentences)

    def _bulk(self, documents, model, embeddings_path, attributes):
        return self._call("bulk", documents, model, embeddings_path, attributes)

    def bulk(self, documents, model="en", batch_size=1000, embeddings_path=None, attributes=None):
        parsed_documents = []
        if len(documents) > batch_size:
            batches = int(math.ceil(len(documents) / batch_size))
            print("Batching {} requests with batch_size {}".format(batches, batch_size))
            if self.verbose:
                batch_iterator = tqdm.tqdm(range(batches))
            else:
                batch_iterator = range(batches)
            for b in batch_iterator:
                docs = documents[b * batch_size:(b + 1) * batch_size]
                res = self._bulk(docs, model, embeddings_path, attributes)
                parsed_documents.extend(res)
        else:
            parsed_documents = self._bulk(documents, model, embeddings_path, attributes)
        return [SpacyClientDocument(x) for x in parsed_documents]
