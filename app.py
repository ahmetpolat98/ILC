from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from datetime import timedelta


# db = SQLAlchemy()
api = Api()
jwt = JWTManager()
ma = Marshmallow()

# def createApp():
app = Flask(__name__)
    
    #this url must be change / local path where the sqlite database is located must be made.
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://ovhhdkypfqxegd:ae2e076df48b2fbf61d26789cda9e6b505a67b56dd194cefa14687421a469c75@ec2-52-211-158-144.eu-west-1.compute.amazonaws.com:5432/deaavsgegkf9a6"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'ILC secret key' 
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

db = SQLAlchemy(app)

    # return app

### ROUTES ###
def addRoutes():
    from controller import UserRegister, Login, Profile, RepoInfo, PasswordChange, OldRepo
    api.add_resource(UserRegister, "/register") #POST ,parameters: email, password ; return: message
    api.add_resource(Login, "/login") #POST ,parameters: email, password ; return: message, access_token (if success)
    api.add_resource(Profile, "/profile") #token required (must be logged-in) | GET, ; return: email, repos[]
    api.add_resource(RepoInfo, "/repo") #token required (must be logged-in) | GET (Get logged in user's repos), ; return:repo[]  | POST (Add repo to logged-in user's repos),  parameters: url ; return: massage
    api.add_resource(PasswordChange, "/password") #token required (must be logged-in) | PATCH (change password logged-in user's), paramaters: old_password, new_password ; return: message
    api.add_resource(OldRepo, "/oldrepo/<int:id>")

# if __name__ == "__main__":
    
    # app = createApp()   
addRoutes()

    # db.init_app(app)
api.init_app(app)
jwt.init_app(app)
ma.init_app(app)
    
CORS(app)
    
    # app.run(host="0.0.0.0", port=8000, debug=True)