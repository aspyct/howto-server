import pytumblr
import json

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
        
        return raw 
        status = raw["meta"]["status"]
        if status == 200:
            return raw
        elif status / 100 == 4:
            return None
        else:
            raise TumblrServerError(raw)


class TumblrServerError(Exception):
    pass

