import flask
from flask import jsonify
from flask import request
from data import db_session
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin

blueprint = flask.Blueprint('users_api', __name__,
                            template_folder='templates')


class User(db_session.SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    email = sqlalchemy.Column(sqlalchemy.String)
    password = sqlalchemy.Column(sqlalchemy.String)
    remember_me = sqlalchemy.Column(sqlalchemy.Boolean)
    city = sqlalchemy.Column(sqlalchemy.String)
    submit = sqlalchemy.Column(sqlalchemy.Boolean)

    def check_password(self, password):
        if password == self.password:
            return True
        return False


#  получение всех пользователей
@blueprint.route('/api/users')
def get_users():
    session = db_session.create_session()
    users = session.query(User).all()
    return jsonify(
        {
            'users':
                [item.to_dict()
                 for item in users]
        }
    )


#  получение одного пользователя по id
@blueprint.route('/api/users/<int:user_id>')
def get_user_id(user_id):
    session = db_session.create_session()
    users = session.query(User).get(user_id)
    if not users:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'users': users.to_dict()
        }
    )


# добавление пользователя
@blueprint.route('/api/users', methods=['POST'])
def create_user():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['id', 'email', 'password', 'remember_me', 'city', 'submit']):
        return jsonify({'error': 'Bad request'})
    session = db_session.create_session()
    if session.query(User).filter(User.id == request.json['id']).first():
        return jsonify({'error': 'Id already exists'})
    user = User(
        id=request.json['id'],
        email=request.json['email'],
        password=request.json['password'],
        remember_me=request.json['remember_me'],
        city = request.json['city'],
        submit=request.json['collaborators']
    )
    session.add(user)
    session.commit()
    return jsonify({'success': 'OK'})


# редактирование пользователя
@blueprint.route('/api/users/<int:user_id>', methods=['POST'])
def edit_jobs(user_id):
    session = db_session.create_session()
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        return jsonify({'error': 'Not found'})
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['id', 'email', 'password', 'remember_me', 'submit']):
        return jsonify({'error': 'Bad request'})
    user.id = request.json['id']
    user.email = request.json['email']
    user.password = request.json['password']
    user.remember_me = request.json['remember_me']
    user.city = request.json['city']
    user.submit = request.json['submit']
    session.commit()
    return jsonify({'success': 'OK'})


# удаление пользователя
@blueprint.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'Not found'})
    session.delete(user)
    session.commit()
    return jsonify({'success': 'OK'})
