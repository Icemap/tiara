from werkzeug.middleware.proxy_fix import ProxyFix

from backend.app import create_app

app = create_app()
app.wsgi_app = ProxyFix(app.wsgi_app)
