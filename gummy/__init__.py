from pyramid.config import Configurator
from sqlalchemy import engine_from_config
import hashlib
import re
from jinja2 import Markup

from .models.db import DBSession, Base


def config_templates(config):
    config.include('pyramid_jinja2')
    config.add_jinja2_search_path("gummy:templates")

    # global globals
    env = config.get_jinja2_environment()

    def avatar(email, size=20):
        m = re.match("(.*) <(.*)>", email)
        if m:
            email = m.group(2)
        h = hashlib.md5(email).hexdigest()
        return Markup('<img class="avatar" width="%d" height="%d" src="https://secure.gravatar.com/avatar/%s?s=%d&d=retro">' % (size, size, h, size))

    def name(author):
        m = re.match("(.*) <(.*)>", author)
        if m:
            author = m.group(1)
        return author

    def score2css(score):
        return {"-2": "no", "-1": "eh", "+1": "ok", "+2": "ja"}[score]

    env.globals['len'] = len
    env.globals['avatar'] = avatar
    env.globals['name'] = name

    # per-request globals
    def add_renderer_globals(event):
        def simple_static_url(name):
            return event["request"].static_url('gummy:static/'+name)
        env.globals['static_url'] = simple_static_url
        env.globals['route_url'] = event["request"].route_url
        env.globals['route_path'] = event["request"].route_path
    config.add_subscriber(add_renderer_globals, 'pyramid.events.BeforeRender')


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)

    config_templates(config)

    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('index', '/')
    config.add_route('project', '/p/{project}')
    config.add_route('branch', '/p/{project}/b/{branch}')
    config.add_route('commit', '/p/{project}/b/{branch}/c/{commit}')
    config.add_route('comment', '/comment')
    config.add_route('misc-pygments', '/misc/pygments.css')

    config.scan()
    return config.make_wsgi_app()
