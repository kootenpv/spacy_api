import tqdm
from cachetools import LRUCache
import math
import numpy as np
from mprpc import RPCClient


class SpacyClientToken():

    def __init__(self, sentence, **kwargs):
        self.attributes = kwargs
        for k, v in kwargs.items():
            if k == "children":
                self.sentence = sentence
                setattr(self, "_children", v)
            else:
                setattr(self, k, v)
        if "vector" in self.attributes:
            self.vector = np.array(self.vector)

    @property
    def children(self):
        tokens = self.sentence.tokens
        return [tokens[x] for x in self._children]

    def __repr__(self):
        if "text" in self.attributes:
            return self.text
        return self.lemma_


class SpacyClientSentence(list):

    def __init__(self, tokens):
        self.tokens = [SpacyClientToken(self, **token) for token in tokens]
        super(SpacyClientSentence, self).__init__(self.tokens)
        self._vector = None

    @property
    def vector(self):
        if self._vector is None:
            self._vector = np.mean([x.vector for x in self.tokens], axis=0)
        return self._vector

    @property
    def string(self):
        return "".join([x.string for x in self.tokens])

    @property
    def text(self):
        return self.string

    @property
    def root(self):
        return self.tokens[self.tokens[0].root]

    def __getitem__(self, i):
        return self.tokens[i]


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

    @property
    def string(self):
        return "".join([x.string for x in self.sents])

    @property
    def text(self):
        return self.string

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


class BaseClient(object):

    def __init__(self, model, embeddings_path):
        self.model = model
        self.embeddings_path = embeddings_path

    def __call__(self, *args, **kwargs):
        return self.single(*args, **kwargs)

    def single(self, document, attributes):
        raise NotImplementedError

    def bulk(self, documents, attributes):
        raise NotImplementedError


class Client(BaseClient):

    def __init__(self, host="127.0.0.1", port=9033, model="en", embeddings_path=None, verbose=False, attributes=None):
        super(Client, self).__init__(model, embeddings_path)
        self.host = host
        self.port = port
        self.rpc = RPCClient(host, port)
        self.verbose = verbose
        self.attributes = attributes
        self.cache = LRUCache(maxsize=3000000)

    def _call(self, path, *args):
        return self.rpc.call(path, *args)

    def most_similar(self, word, n=10):
        key = (word, n, self.model, self.embeddings_path)
        if key not in self.cache:
            result = self._call("most_similar", word, n, self.model, self.embeddings_path)
            self.cache[key] = result
        return self.cache[key]

    def single(self, document, attributes=None):
        attributes = attributes or tuple(self.attributes)
        key = (document, attributes, self.model, self.embeddings_path)

        if key not in self.cache:
            sentences = self._call("single", document, self.model,
                                   self.embeddings_path, attributes)
            result = SpacyClientDocument(sentences)
            self.cache[key] = result
            return result

        return self.cache[key]

    def _bulk(self, documents, attributes):
        attributes = attributes or tuple(self.attributes)
        done_docs = [(num, self.cache[(document, attributes)]) for num, document in enumerate(documents)
                     if (document, attributes) in self.cache]
        todo_docs = [(num, document) for num, document in enumerate(documents)
                     if (document, attributes) not in self.cache]
        todo_inds = [x[0] for x in todo_docs]
        todo_docs = [x[1] for x in todo_docs]
        if todo_docs:
            print(todo_docs)
            todo_docs = self._call("bulk", todo_docs, self.model, self.embeddings_path, attributes)
        todo_docs = [(x, SpacyClientDocument(y)) for x, y in zip(todo_inds, todo_docs)]
        return [x[1] for x in sorted(todo_docs + done_docs)]

    def bulk(self, documents, batch_size=1000, attributes=None):
        attributes = attributes or tuple(self.attributes)
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
                res = self._bulk(docs, attributes)
                parsed_documents.extend(res)
        else:
            parsed_documents = self._bulk(documents, attributes)
        return parsed_documents
