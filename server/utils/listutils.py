def listDiff(a, b):
    b = set(b)
    return [aa for aa in a if aa not in b]