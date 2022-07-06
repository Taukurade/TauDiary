
import secrets
from datetime import datetime as dt
from quart import Quart, render_template, request, redirect, url_for
from quart_auth import AuthUser, AuthManager, login_required, login_user, logout_user, Unauthorized
from peewee import *

app = Quart('TauDiary',template_folder='.',static_folder='.')
app.secret_key = secrets.token_urlsafe(32) 
db = SqliteDatabase('my_data.db')
AuthManager(app)

class mdl(Model):
    class Meta:
        database = db

class Users(mdl):
    login = TextField(unique=True)
    password = TextField()

class Diary(mdl):
    title = TextField()
    text = TextField()
    mood = TextField()
    date = DateField(default=dt.now,formats=['%d.%m.%Y %H:%M'])

db.create_tables([Diary,Users])



@app.route('/')
@login_required
async def main_page():
    diary = Diary.select()
    return await render_template('diary.html',diary=diary)


@app.route('/diary_delete/<int:id>')
@login_required
async def diary_delete(id):
    Diary.delete_by_id(id)
    return redirect(url_for('main_page'))

@app.route('/diary',methods=['GET','POST'])
@login_required
async def diary_upload():
    if request.method == 'POST':
        try:
            data = await request.form
            title = data['title']
            mood = data['mood']
            text = data['text']
        except KeyError:
            return await render_template('admin.html',err='Какое-то из полей не было заполнено.')
        
        Diary.create(title=title, mood=mood,text=text)

  
        return await render_template('admin.html',err='успешно')
    if request.method == 'GET':
        return await render_template('admin.html',err='')

@app.route('/login',methods=['GET','POST'])
async def login():
    if request.method == 'POST':
        data = await request.form
        print(data['login'])
        login = data['login']
        password = data['password']
        user = Users.select().where((Users.login == login) & (Users.password == password)).get_or_none()
        if user is None:
            return {'error':'No such user'}
        login_user(AuthUser(user.id))
        return redirect(url_for('diary_upload'),302)
    if request.method == 'GET':
        return await render_template('login.html')
@app.route('/logout')
@login_required
async def logout():
    logout_user()
    return redirect(url_for('login'),302)

@app.errorhandler(Unauthorized)
async def redirect_to_login(*_):
    return redirect(url_for("login"))

@app.errorhandler(404)
async def NotFoundError(*_):
    return redirect('/')


app.run('0.0.0.0',80)