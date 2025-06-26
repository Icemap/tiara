from flask_cors import CORS


def init_cors(app):
    cors = CORS(
        app,
        resources={
            r"/api/*": {
                "origins": [
                    r"https://(.*\.)?tidb\.ai$",
                    "http://localhost:3000"
                ]
            }
        },
        supports_credentials=True
    )
