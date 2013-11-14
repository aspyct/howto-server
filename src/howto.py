import pytumblr
import json
from HTMLParser import HTMLParser

def exposed(obj):
    obj.exposed = True
    return obj


def json_endpoint(obj):
    def json_wrapper(*args, **kwargs):
        result = obj(*args, **kwargs)
        return json.dumps(result)
    
    return exposed(json_wrapper)


class Server(object):
    def __init__(self, config):
        self._blog = HowToClient(config['tumblr'])

    @json_endpoint
    def index(self):
        return self._blog.info()

    @json_endpoint
    def post(self, post_id):
        return self._blog.post(post_id)


class HowToClient(object):
    # IMPORTANT: never put a `exposed` attribute on this class
    def __init__(self, config):
        self.blogname = config['blog']
        self.tumblr = pytumblr.TumblrRestClient(
            config['key'],
            config['secret']
        )
        self.tag = config['tag']
    
    def info(self):
        return self.tumblr.blog_info(self.blogname)

    def post(self, post_id):
        raw = self.tumblr.posts(self.blogname,
            id = post_id
        )
        
        if 'posts' in raw:
            # We have it !
            return self.format_post(raw['posts'][0])
        else:

            status = raw["meta"]["status"]
            if status / 100 == 4:
                return None
            else:
                raise TumblrServerError(raw)

    def format_post(self, raw_post):
        if self.is_howto(raw_post):

            post = {
                'url': raw_post['short_url'],
            }

            post['name'], post['steps'] = self.parse_body(raw_post)

            return post
        else:
            raise PostIsNotHowtoException()

    def parse_body(self, raw_post):
        text = raw_post['caption']

        if raw_post['format'] == 'html':
            text = strip_tags(text)

        return 'hello', text
    
    def is_howto(self, raw_post):
        return self.tag in raw_post['tags'] and raw_post['type'] == 'photo'


class PostIsNotHowtoException(Exception):
    pass

class TumblrServerError(Exception):
    pass


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

