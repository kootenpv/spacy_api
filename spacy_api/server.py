from gevent.server import StreamServer
from mprpc import RPCServer
from spacy_api.api import single, bulk


class SpacyServer(RPCServer):

    def single(self, document, model, embeddings_path, attributes):
        return single(document, model, embeddings_path, attributes)

    def bulk(self, documents, model, embeddings_path, attributes):
        documents = tuple(documents)
        return bulk(documents, model, embeddings_path, attributes)


def serve(host="127.0.0.1", port=9033):
    server = StreamServer((host, int(port)), SpacyServer())
    server.serve_forever()

if __name__ == "__main__":
    serve()
