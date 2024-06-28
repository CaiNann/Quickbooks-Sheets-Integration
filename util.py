def format_date(rawDate):
    indexOfT = rawDate.index('T')
    newDate = rawDate[0:indexOfT]
    return newDate