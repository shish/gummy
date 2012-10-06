from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models.db import (
    DBSession,
    Base,
    )


def config_templates(config):
    config.include('pyramid_jinja2')
    config.add_jinja2_search_path("gummy:templates")
    def add_renderer_globals(event):
        def simple_static_url(name):
            return event["request"].static_url('gummy:static/'+name)
        event['static_url'] = simple_static_url
        event['route_url'] = event["request"].route_url
        event['route_path'] = event["request"].route_path
        event['len'] = len
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

    config.scan()
    return config.make_wsgi_app()

