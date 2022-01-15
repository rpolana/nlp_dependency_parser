from main import app

import pprint


class LoggingMiddleware(object):
    def __init__(self, app):
        self._app = app

    def __call__(self, env, resp):
        errorlog = env['wsgi.errors']
        pprint.pprint(('REQUEST', env), stream=errorlog)

        def log_response(status, headers, *args):
            pprint.pprint(('RESPONSE', status, headers), stream=errorlog)
            return resp(status, headers, *args)

        return self._app(env, log_response)


if __name__ == "__main__":
    from waitress import serve
    # app.wsgi_app = LoggingMiddleware(app.wsgi_app)
    serve(app, host="0.0.0.0", port=5000)
