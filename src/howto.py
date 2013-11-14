import pytumblr
import json
from HTMLParser import HTMLParser
import re

def exposed(obj):
    obj.exposed = True
    return obj


def json_endpoint(obj):
    def json_wrapper(*args, **kwargs):
        result = obj(*args, **kwargs)
        return json.dumps(result)
    
    return exposed(json_wrapper)


class Server:
    def __init__(self, config):
        self.v1 = ServerV1(config)


class ServerV1(object):
    def __init__(self, config):
        self._blog = HowToClient(config['tumblr'])

    @json_endpoint
    def index(self):
        return self._blog.info()

    @json_endpoint
    def post(self, post_id):
        return self._blog.post(post_id)


class HowToClient(object):
    # IMPORTANT: never put an `exposed` attribute on this class
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
        self.validate_howto(raw_post)

        post = {
            'url': raw_post['short_url'],
        }

        post['name'], post['steps'] = self.parse_body(raw_post)

        return post

    def parse_body(self, raw_post):
        text = raw_post['caption']

        if raw_post['format'] == 'html':
            parser = HowtoHtmlParser()
        else:
            raise ValueError("Can only parse HTML bodies for now")

        return parser.parse(text)
    
    def validate_howto(self, raw_post):
        if self.tag and self.tag not in raw_post['tags']:
            raise CannotParseHowtoException('Does not contain the adequate tag')

        if raw_post['type'] != 'photo':
            raise CannotParseHowtoException('Not a photo post')


class HowtoHtmlParser(object):
    def parse(self, text):
        text = strip_tags(text)

        # first, parse the title
        # i.e. take everything until the first step
        end = text.find('1.')

        if end == -1:
            raise CannotParseHowtoException("No first step found")

        stepgen = self.step_generator(text)

        title = next(stepgen)
        steps = list(stepgen)

        return title, steps

    def step_generator(self, text):
        start_pos = 0
        next_step = 1
        
        while 1:
            pattern = r'\s*0?{}\.\s*'.format(next_step)
            matcher = re.compile(pattern)

            match = matcher.search(text, start_pos)
            if match is None:
                yield text[start_pos:].rstrip()
                break
            else:
                start, end = match.span()
                yield text[start_pos:start]
                start_pos = end
                next_step += 1

class CannotParseHowtoException(Exception):
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

