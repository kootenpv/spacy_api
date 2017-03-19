
def nodef(node, level):
    tmpl = "\n{} {}\t({},\t{})"
    return tmpl.format("----" * level, node.text, node.pos_, node.dep_)


def str_tree(tree, level=0):
    children = list(tree.children)
    s = nodef(tree, level)
    if len(children) == 0:
        return s
    else:
        return s + "".join(str_tree(child, level + 1) for child in children)


def get_tree(sentence, nlp):
    for sent in nlp(sentence).sents:
        txt = sent.text
        yield next(nlp(txt[0].upper() + txt[1:]).sents)


def repr_tree(sentence, nlp):
    res = ""
    for tr in get_tree(sentence, nlp):
        res += "\nInput: " + tr.text
        res += "\n" + str_tree(tr.root)
    return res
