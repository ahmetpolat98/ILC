from app import db, ma
from passlib.apps import custom_app_context as pwd_context
from marshmallow_sqlalchemy.fields import Nested
from marshmallow import fields

class User(db.Model):
    userId = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    surname = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    github_username = db.Column(db.String(80))
    created_date = db.Column(db.DateTime)
    repos = db.relationship('Repo', backref='user', lazy=True)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def add_repo(self, repo:'Repo'):
        self.repos.append(repo)
        db.session.commit()

    def hash_password(self, password):
        self.password = password
        # self.password = pwd_context.encrypt(password)

    def verify_password(self, password):
        if self.password == password:
            return True
        else:
            return False
        # return pwd_context.verify(password, self.password)

    def commit(self):
        db.session.commit()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(userId=_id).first()


class Repo(db.Model):
    repoId = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.userId'), nullable=False)
    url = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(80))
    isChecked = db.Column(db.Boolean, nullable=False, default=False)
    added_date = db.Column(db.DateTime)
    updated_date = db.Column(db.DateTime)
    checks = db.relationship('Check', backref='repo', lazy=True)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def add_check(self, check:'Check'):
        self.checks.append(check)
        db.session.commit()

    def commit(self):
        db.session.commit()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(repoId=_id).first()
    

class Check(db.Model):
    checkId = db.Column(db.Integer, primary_key=True)
    repoId = db.Column(db.Integer, db.ForeignKey('repo.repoId'), nullable=False)
    check_date = db.Column(db.DateTime)
    inconsistency = db.Column(db.Text)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def commit(self):
        db.session.commit()

class CheckSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Check
        load_instance = True
        include_fk = True
        exclude = ("check_date",)

class RepoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Repo
        include_fk = True
        include_relationships = True
        load_instance = True
        exclude = ("added_date","language", "updated_date", )
    
    checks = Nested(CheckSchema, many=True)

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True
        load_instance = True
        exclude = ("password","created_date", "github_username")

    repos = Nested(RepoSchema, many=True)



if __name__ == "__main__":
    print("Creating database tables...")
    # Check.__table__.drop(db.engine)
    # Repo.__table__.drop(db.engine)
    # db.drop_all()
    db.create_all()
    print("Done!")