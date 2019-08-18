def dict_from_row(row):
    return dict(zip(row.keys(), row))

def dict_from_rows(rows):
    outlist=[]
    for row in rows:
        outlist.append(dict_from_row(row))
    return outlist