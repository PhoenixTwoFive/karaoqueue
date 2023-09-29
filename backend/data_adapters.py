def dict_from_rows(rows):
    outlist = []
    for row in rows:
        outlist.append(dict(row._mapping))
    return outlist
