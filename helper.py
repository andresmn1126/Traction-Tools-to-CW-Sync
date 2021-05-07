def shorten_name(str):
    l = str.split()
    first_name = l[0]
    last_name = l[1]
    new = first_name[0].lower() + last_name.lower()
    return new   

def turn_to_lower(str):
    lowercase = str.lower()
    return lowercase

def merge_list_of_dicts(ttlist, cwlist):
    result = []
    for dict1 in ttlist:
        for dict2 in cwlist:
            if dict1['name'] in dict2['name']:
                dict1['cwid'] = dict2['cwid']
                result.append(dict1)
    return result