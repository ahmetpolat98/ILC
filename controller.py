from flask_restful import Resource, reqparse
from flask import jsonify
from models import *
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import checker
import json


class UserRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('email', type=str, help="Email is required", required=True)
    parser.add_argument('password', type=str, help="Password is required", required=True)

    def post(self):
        data = UserRegister.parser.parse_args()
        if User.find_by_email(data['email']):
            return {'message': 'Email has already been taken'}, 400
        user = User(**data)
        user.hash_password(data['password'])
        user.save_to_db()
        return {'message':  'User has been created successfully'}, 201


class Login(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('email', type=str, help="Email is required", required=True)
    parser.add_argument('password', type=str, help="Password is required", required=True)

    def post(self):
        data = Login.parser.parse_args()
        user = User.find_by_email(data['email'])
        if not user or not user.verify_password(data['password']):
            return {'message': 'Wrong Email or Password'}, 404
        access_token = create_access_token(identity=data['email'])
        return jsonify(message="Login Succeeded!", access_token=access_token)


class Profile(Resource):

    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        user = User.find_by_email(current_user)
        user_schema = UserSchema()
        output = user_schema.dump(user)
        return jsonify(output)


class RepoInfo(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('url', type=str, help="URL is required", required=True)
    parser.add_argument('dev', type=str, help="Dev is required", required=True)

    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        user = User.find_by_email(current_user)
        repo_schema = RepoSchema(many=True)
        output = repo_schema.dump(user.repos)
        return jsonify(output)

    @jwt_required()
    def post(self):
        data = RepoInfo.parser.parse_args()
        current_user = get_jwt_identity()
        user = User.find_by_email(current_user)
        repo = Repo(url = data["url"], userId=user.userId)
        repo.save_to_db()
        user.add_repo(repo)

        dev = data["dev"]
        devdep = dev
  
        output = checker.ILC(data["url"], False)
        # output = {'name': 'aws-sdk-js', 'attributes': {'license': 'apache-2.0', 'color': 'y'}, 'children': [{'name': 'buffer', 'attributes': {'license': 'mit', 'color': 'y'}, 'children': [{'name': 'base64-js', 'attributes': {'license': 'mit', 'color': 'y'}}, {'name': 'ieee754', 'attributes': {'license': 'bsd-3-clause', 'color': 'n'}}]}, {'name': 'events', 'attributes': {'license': 'mit', 'color': 'y'}}, {'name': 'ieee754', 'attributes': {'license': 'bsd-3-clause', 'color': 'y'}}, {'name': 'jmespath', 'attributes': {'license': 'other', 'color': '?'}}, {'name': 'querystring', 'attributes': {'license': 'mit', 'color': 'y'}}, {'name': 'sax', 'attributes': {'license': 'other', 'color': '?'}}, {'name': 'url', 'attributes': {'license': 'mit', 'color': 'y'}, 'children': [{'name': 'punycode', 'attributes': {'license': 'mit', 'color': 'y'}}, {'name': 'querystring', 'attributes': {'license': 'mit', 'color': 'y'}}]}, {'name': 'uuid', 'attributes': {'license': 'mit', 'color': 'y'}}, {'name': 'xml2js', 'attributes': {'license': 'mit', 'color': 'y'}}]}

        json_string = json.dumps(output,skipkeys = True,allow_nan = True) #json to string

        check = Check(repoId=repo.repoId, inconsistency=json_string)
        check.save_to_db()
        repo.add_check(check)

        out_json = json.loads(json_string) #string to json
        return jsonify(out_json)


#old repo, get old repos check and update repo's check
class OldRepo(Resource):
    parser = reqparse.RequestParser()
    # parser.add_argument('url', type=str, help="URL is required", required=True)
    parser.add_argument('dev', type=str, help="Dev is required", required=True)

    @jwt_required()
    def get(self, id): #sorun: başka userın reposuna istek atılabiliyor
        repo = Repo.find_by_id(id)
        if not repo:
            return {"message": "Repo Not Found"}, 404
        out_json = json.loads(repo.checks[0].inconsistency) #string to json
        return jsonify(out_json)

    def post(self, id):
        data = OldRepo.parser.parse_args()
        repo = Repo.find_by_id(id)
        if not repo:
            return {"message": "Repo Not Found"}, 404
        
        dev = data["dev"]
        devdep = dev

        output = checker.ILC(repo.url, devdep)

        json_string = json.dumps(output,skipkeys = True,allow_nan = True) #json to string

        repo.checks[0].inconsistency = json_string
        repo.commit()

        return jsonify(output)

#change password
class PasswordChange(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('old_password', type=str, help="Old Password is required", required=True)
    parser.add_argument('new_password', type=str, help="New Password is required", required=True)

    @jwt_required()
    def post(self):
        data = PasswordChange.parser.parse_args()
        current_user = get_jwt_identity()
        user = User.find_by_email(current_user)

        if not user.verify_password(data['old_password']):
            return {'message': 'Currently Password is wrong'}, 404
        user.hash_password(data['new_password'])
        user.commit()
        return {'message':  'Password changed successfully'}, 200


