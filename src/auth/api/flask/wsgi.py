from auth.api.flask.app import create_app
from auth.bootstrap import FlaskContainer

app = create_app(FlaskContainer)
