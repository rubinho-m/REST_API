from data import db_session
import sqlalchemy
import user_api
from user_api import User
from flask import Flask, redirect, render_template, request, jsonify, make_response
from flask_login import LoginManager, UserMixin, login_user, login_required
from flask_wtf import FlaskForm
from sqlalchemy_serializer import SerializerMixin
from wtforms import SubmitField, PasswordField, BooleanField, StringField
from wtforms.validators import DataRequired
from data.news import NewsForm
from requests import get
from get_img import get_img

global_user = None


class News(db_session.SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'news'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    text = sqlalchemy.Column(sqlalchemy.String)
    team_lead = sqlalchemy.Column(sqlalchemy.String)
    work_size = sqlalchemy.Column(sqlalchemy.String)
    collaborators = sqlalchemy.Column(sqlalchemy.String)


class LoginForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    city = StringField('Родной город', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


def logout_user():
    global global_user
    global_user = None


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit() and form.password_again.data == form.password.data:
        db_session.global_init('db/mars_one.db')
        session = db_session.create_session()
        user = User()
        user.email = form.email.data
        user.password = form.password.data
        user.city = form.city.data
        session.add(user)
        session.commit()
        return redirect("/")
    return render_template('register.html', form=form, current_user=None)


@app.route('/')
@app.route('/index')
def index():
    db_session.global_init('db/mars_one.db')
    session = db_session.create_session()
    news = session.query(News).all()
    return render_template('base.html', title='Главная', current_user=global_user, news=news,
                           start=True, nostalgy=True)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    session = db_session.create_session()
    news = session.query(News).filter(News.id == id,
                                      News.team_lead == global_user.id).first()
    if request.method == "GET":
        if news:
            form.title.data = news.text
            form.teamlead_id.data = news.team_lead
            form.work_size.data = news.work_size
            form.collaborators.data = news.collaborators
    if form.validate_on_submit():
        news.text = form.title.data
        news.team_lead = form.teamlead_id.data
        news.work_size = form.work_size.data
        news.collaborators = form.collaborators.data
        session.commit()
        return redirect('/')

    return render_template('news.html', title='Редактирование новости', form=form)


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    session = db_session.create_session()
    news = session.query(News).filter(News.id == id,
                                      News.team_lead == global_user.id).first()
    if news:
        session.delete(news)
        session.commit()
    return redirect('/')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@login_manager.user_loader
def load_user(user_id):
    db_session.global_init('db/mars_one.db')
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    global global_user
    form = LoginForm()
    if form.validate_on_submit():
        db_session.global_init('db/mars_one.db')
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            global_user = user
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form, current_user=None)


@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        news = News()
        news.text = form.title.data
        news.team_lead = form.teamlead_id.data
        news.work_size = form.work_size.data
        news.collaborators = form.collaborators.data
        session = db_session.create_session()
        session.add(news)
        session.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости',
                           form=form)


@app.route('/users_show/<int:user_id>')
def show(user_id):
    user = get(f'http://localhost:5000/api/users/{user_id}').json()
    city = user['users']['city']
    email = user['users']['email']
    image = get_img(city)
    return render_template('nostalgy.html', title='Ностальгия', city=city, email=email, image=image)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


def main():
    db_session.global_init("db/mars_one.db")
    app.register_blueprint(user_api.blueprint)
    app.run()


if __name__ == '__main__':
    main()
