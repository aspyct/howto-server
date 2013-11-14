import pytumblr

def exposed(obj):
    obj.exposed = True
    return obj

class Server(object):
    def __init__(self):
        self._client = pytumblr

    @exposed
    def index(self):
        return "Hello dude !"


@exposed
class Post(object):
    def GET(self):
        return "You accessed me via GET"

