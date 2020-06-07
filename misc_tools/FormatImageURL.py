import urllib


def format_image_url(raw_url):
    clean_url = urllib.parse.unquote_plus(raw_url)
    urllib.parse.unquote_plus(clean_url)
    clean_url = clean_url[:-1]
    clean_url = clean_url.replace('image://', 'image%3A%2F%2F')
    clean_url = clean_url.replace('http://', 'http%253a%252f%252f')
    clean_url = clean_url.replace('/', '%252f')
    clean_url = clean_url.replace(' ', '%2520')
    return clean_url
