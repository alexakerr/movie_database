import os
from flask import Flask
from app.models import db
from flask_migrate import Migrate
from app.schema import schema
from graphql_server.flask import GraphQLView

app = Flask(__name__)

# configures the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

# initializes the database
db.init_app(app)

# initialize Flask-Migrate
migrate = Migrate(app, db)

# adds GraphQL endpoint **
app.add_url_rule('/graphql', view_func=GraphQLView.as_view(
    'graphql',
    schema=schema,
    graphiql=True
))

# the home route
@app.route('/')
def index():
    return "Hello, welcome to the GraphQL API!"