from flask import Flask
from flask import request
from flask import jsonify

from spacy_api.cors import crossdomain
from spacy_api.api import single, bulk

app = Flask(__name__)


def get_args():
    if request.method == "POST":
        args = request.json
    else:
        args = request.args
    return args


@app.route("/single", methods=["GET", "POST", "OPTIONS"])
@crossdomain(origin='*', headers="Content-Type")
def single_route():
    args = get_args()
    document = args.get("document", "")
    attributes = args.get("attributes", None)
    if attributes is None:
        attributes = "text,lemma_,pos_,tag_"
    atts = tuple(attributes.split(","))
    model = args.get("model", "en")
    embeddings_path = args.get("embeddings_path", None)
    return jsonify(single(document, attributes=atts, model=model, embeddings_path=embeddings_path))


@app.route("/bulk", methods=["POST", "OPTIONS"])
@crossdomain(origin='*', headers="Content-Type")
def bulk_route():
    args = get_args()
    documents = args.get("documents", [""])
    attributes = args.get("attributes", None)
    if attributes is None:
        attributes = "text,lemma_,pos_,tag_"
    atts = tuple(attributes.split(","))
    model = args.get("model", "en")
    embeddings_path = args.get("embeddings_path", None)

    parsed_docs = bulk(documents, attributes=atts,  model=model,
                       embeddings_path=embeddings_path)
    return jsonify(parsed_docs)


def serve(host="127.0.0.1", port=9033):
    app.run(host=host, port=int(port))

if __name__ == "__main__":
    serve()
