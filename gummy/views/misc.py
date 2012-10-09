from pyramid.view import view_config
from pygments.formatters import HtmlFormatter


@view_config(route_name='misc-pygments', renderer='string')
def misc_pygments(request):
    return HtmlFormatter().get_style_defs('.highlight')
