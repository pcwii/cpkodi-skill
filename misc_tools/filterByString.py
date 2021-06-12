def filter_by_string(query, options, key=(lambda x: x)):
    query = query.lower().split(' ')
    options = [(key(option).lower(), option) for option in options]
    def sortkey(option):
        return (- sum(term in option[0] for term in query))
    matching_list = []
    for name, item in options:
        if any(term in name for term in query):
            matching_list.append((name, item))
    return([x[1] for x in sorted(matching_list, key=sortkey)])