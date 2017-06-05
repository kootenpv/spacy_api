
class TreeView(object):

    def __init__(self, nlp, text="text", attrs="i, pos_, dep_, tag_, ent_type_"):
        self.nlp = nlp
        self.text = text
        self.attrs = attrs

    def __repr__(self):
        attrs = ", ".join(self._attrs)
        return '{}(text="{}", attrs="{}")'.format(self.__class__.__name__, self.text, attrs)

    @property
    def _attrs(self):
        if isinstance(self.attrs, str):
            self.attrs = self.attrs.replace(" ", "").split(",")
        return self.attrs

    def node_format(self, node, level):
        tmpl_args = "(" + ",\t".join(["{}"] * len(self._attrs)) + ")"
        tmpl = "\n{} {}\t" + tmpl_args
        return tmpl.format("----" * level, *[getattr(node, x) for x in [self.text] + self._attrs])

    def dump_tree(self, tree, level=0):
        children = list(tree.children)
        s = self.node_format(tree, level)
        if not children:
            return s
        return s + "".join(self.dump_tree(child, level + 1) for child in children)

    def get_sentences(self, text_or_doc):
        doc = self.nlp(text_or_doc) if isinstance(text_or_doc, str) else text_or_doc
        for sentence in doc.sents:
            txt = sentence.text
            yield next(self.nlp(txt[0].upper() + txt[1:]).sents)

    def get_first(self, text):
        return next(self.get_sentences(text)).root

    def print(self, text_or_doc):
        print(self.dump(text_or_doc))

    def dump(self, text_or_doc):
        res = ""
        sentences = self.get_sentences(text_or_doc)
        for sentence in sentences:
            res += "\nInput: " + sentence.text
            res += "\n" + self.dump_tree(sentence.root)
        return res

    def find(self, node, fn, res=None, it=0):
        res = self.findall(node, fn, res, it)
        return res[0] if res else None

    def findall(self, node, fn, res=None, it=0):
        if isinstance(node, str):
            node = self.nlp(node)
        if it == 0:
            res = []
        if hasattr(node, "sents"):
            for sent in node.sents:
                self.findall(sent.root, fn, res, 1)
        else:
            if fn(node):
                res.append((node, it))
            if hasattr(node, "children"):
                for child in node.children:
                    self.findall(child, fn, res, it + 1)
        target = [y[0] for y in sorted(res, key=lambda x: x[1])] or None
        return target
