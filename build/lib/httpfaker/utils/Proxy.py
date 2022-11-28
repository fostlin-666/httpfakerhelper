# coding: utf-8
# 本文件参考了flask_Proxy库
# https://github.com/mecforlove/flask-proxy


import requests
from urllib import parse
from flask import request, Response


class Proxy(object):
    def __init__(self, app=None):
        self.upstreams = []
        self.init_app(app)

    def init_app(self, app):
        """Initialize this class with the given :class:`flask.Flask`
        application.

        :param app: the Flask application
        :type app: flask.Flask
        """
        self.app = app

    def add_upstream(self, upstream):
        """Add a upstream to the proxy.

        """
        endpoint = getattr(upstream, 'endpoint',
                           None) or upstream.__name__.lower()
        upstream.endpoint = endpoint
        self.upstreams.append(upstream)
        view_func = upstream.as_view()
        if upstream.decorators:
            for dec in upstream.decorators:
                view_func = dec(view_func)
        for route in upstream.routes:
            rule = upstream.prefix + route['url']
            self.app.add_url_rule(
                rule,
                endpoint=endpoint,
                view_func=view_func,
                methods=route['methods'])


class Upstream(object):
    host = None
    scheme = None
    port = None
    decorators = None
    params = None
    timeout = None
    local_headers = None

    @staticmethod
    def _get_attr(attr, default=None):
        if callable(attr):
            return attr() or default
        return attr or default

    @classmethod
    def as_view(cls):
        def _view(*args, **kwargs):
            url_info = parse.urlparse(request.url)
            ogrin_host = url_info.netloc
            proxy_url = cls._get_attr(cls.host)
            proxy_host = parse.urlparse(proxy_url).netloc
            params = {}
            if url_info.query:
                [params.update({x[0]: x[1]}) for x in parse.parse_qsl(url_info.query, True)]
            timeout = cls._get_attr(cls.timeout)
            method = request.method
            uri = url_info.path
            url = proxy_url + uri
            headers = dict(request.headers)
            headers['Host'] = proxy_host
            headers.update(cls.local_headers)
            if 'Referer' in headers:
                headers['Referer'] = headers['Referer'].replace(ogrin_host, proxy_host)
            if 'Origin' in headers:
                headers['Origin'] = headers['Origin'].replace(ogrin_host, proxy_host)
            data = request.get_data() if request.get_data() else None
            resp = requests.request(
                method,
                url,
                params=params,
                headers=headers,
                data=data,
                stream=True,
                timeout=timeout)
            resp_data = resp.raw.read()
            return Response(resp_data, resp.status_code,
                            dict(resp.headers))

        return _view
