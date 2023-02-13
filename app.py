from flask import Flask
from flask_jwt_extended import JWTManager
from database.db import initialize_db
from flask_restful import Api
from resources.routes import initialize_routes
from resources.errors import errors
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'host': 'mongodb://localhost:27017/GroupDatabase'
}
app.config['JWT_SECRET_KEY'] = 't1NP63m4wnBg6nyHYKmc2TpCORGI4nss'

api = Api(app, errors=errors)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

initialize_db(app)
initialize_routes(api)


if __name__ == "__main__":
    app.run()
