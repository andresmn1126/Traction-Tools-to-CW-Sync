def shorten_name(str):
    l = str.split()
    first_name = l[0]
    last_name = l[1]
    new = first_name[0].lower() + last_name.lower()
    return new   