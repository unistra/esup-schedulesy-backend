import re

def authorized_views_preprocessing_hook(endpoints):
    authorized = (r'Building',)
    filtered = []

    for endpoint in endpoints:
        path, path_regex, method, callback = endpoint
        name = callback.__name__
        if any(re.search(a, name) for a in authorized):
            filtered.append(endpoint)
    return filtered