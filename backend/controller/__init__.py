from . import root
from . import github
from . import issues

BPS = [
    ('/', root.bp),
    ('/issues', issues.bp),
]

def init_routes(app):
    github.init_webhook(app)
    for url_prefix, bp in BPS:
        app.register_blueprint(bp, url_prefix=url_prefix)
    return app
