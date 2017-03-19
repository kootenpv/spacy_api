import json
import os

from flask import Flask
from flask import request
from flask import jsonify

from spacy_api.cors import crossdomain
from spacy_api.api import single, bulk, get_nlp
from spacy_api.view_tree import repr_tree

# from spacy_tree import prep
# from spacy_tree import dumptree

PORT = int(os.environ.get("PORT", 9033))

html = """
<html>
    <body style="margin: 0px">
        <div>
                <div style="margin-left: 15%; margin-right: 15%; margin-top:3%">
                <h2>spacy_api</h2>
                <hr>
                <p><h3>Parse:</h3></p>
                <form action="/single" method="get">
                    <p>Input: <input type="text" name="document" value="{document}" style=" width: 50%; border-radius: 4px; box-shadow: silver 3px 3px 2px; padding: 3px;" /></p>
                    <p>Attributes: <input type="text" name="attributes" value="{attributes}" /></p>
                    <input type="hidden" name="results_single" value="{results_single}">
                    <input type="submit" value="Submit" style="margin-top: 10px;">
                </form>

                <p>Result: <code style='white-space: pre-wrap;'>{results_single}</code></p>

                <p><h3>View dependency tree</h3></p>
                <form action="/view_tree" method="get">
                    <p>Input: <input type="text" name="document" value="{document}" style=" width: 50%; border-radius: 4px; box-shadow: silver 3px 3px 2px; padding: 3px;" /></p>
                    <p>Attributes: <input type="text" name="attributes" value="{attributes}" /></p>
                    <input type="hidden" name="results_tree" value="{results_tree}">
                    <input type="submit" value="Submit" style="margin-top: 10px;">
                </form>

                <p>Result: <code style='white-space: pre-wrap;'>{results_tree}</code></p>
            </div>
        </div>
    </body>
</html>
"""

app = Flask(__name__)


def get_args():
    if request.method == "POST":
        args = request.json
    else:
        args = request.args
    return args


@app.route("/enrich", methods=["GET"])
def enrich():
    pass


@app.route("/view_tree", methods=["GET"])
def view_tree():
    args = get_args()
    document = args.get("document", "")
    attributes = args.get("attributes", None)
    results_single = args.get("results_single", "")
    if attributes is None:
        attributes = "text,lemma_,pos_,tag_"
    return html.format(document=document, attributes=attributes, results_single=results_single, results_tree=repr_tree(document, get_nlp()))


@app.route("/", methods=["GET", "POST", "OPTIONS"])
@crossdomain(origin='*', headers="Content-Type")
def root():
    return '<html><body><a href="/single">/single</a><br><a href="/bulk">/bulk (only POST)</a></body></html>'


@app.route("/single", methods=["GET", "POST", "OPTIONS"])
@crossdomain(origin='*', headers="Content-Type")
def single_route():
    args = get_args()
    document = args.get("document", "")
    attributes = args.get("attributes", None)
    if attributes is None:
        attributes = "text,lemma_,pos_,tag_"
    atts = tuple(attributes.split(","))
    if request.method == "GET":
        results_tree = args.get("results_tree", "")
        results = single(document, attributes=atts) if document else "no document was given"
        return html.format(document=document, attributes=attributes, results_tree=results_tree, results_single=json.dumps(results, indent=4))
    elif request.method == "POST":
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
