import os
import functools
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename

from itsdangerous import URLSafeTimedSerializer, SignatureExpired

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

UPLOAD_FOLDER='images'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

S = URLSafeTimedSerializer('dasfegrhrdaUYUHHNJ&@IUJ')
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/')
def init():
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None and user is not None:
            session.clear()
            session['user_id']=user['id']
            session['picture']=user['profile_picture']
            print (session['picture'])

            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS    

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@bp.route('/<int:id>/profile')
def profile(id):
    db = get_db()
    posts=db.execute('SELECT * FROM post WHERE author_id = ?', (id,)).fetchall()
    ans1=db.execute('SELECT * FROM answer WHERE author_id = ?', (id,)).fetchall()
    result=db.execute('SELECT * FROM user WHERE id = ?', (id,)).fetchone()
    ans=[]
    for i in ans1:
        ans.append(db.execute('SELECT * FROM post p JOIN user u ON p.author_id=u.id WHERE qid = ?', (i['qid'],)).fetchone())
    return render_template('auth/profile.html',result=result,posts=posts,ans=ans)

@bp.route('/<int:id>/update_profile', methods=('GET', 'POST'))
def update_profile(id):
    user=get_user(id)
    profile_picture=g.user['profile_picture']
    if request.method =='POST':
        body = request.form['description_body']
        if 'file' in request.files:
            file =request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(os.getcwd()+"/flaskr/static/images/", filename))
                profile_picture=os.path.join(UPLOAD_FOLDER, filename)
                print(profile_picture)
            else:
                print ("format not allowed")
        else:
            print("no file received")
        error = None
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE user SET description = ? ,profile_picture=?'
                ' WHERE id = ?',
                (body,profile_picture, id)
            )
            db.commit()
            user=get_user(id)
            session['picture']=user['profile_picture']
            return redirect(url_for('auth.profile',id=id))
    return render_template('auth/update_profile.html',user_data=user)

@bp.errorhandler(404)
def page_not_found(e):
    return render_template('auth/404.html'), 404

def get_user(id):
    user = get_db().execute('select * from user where id=?',(id,)).fetchone()
    if user is None:
        abort(404, "User id {0} doesn't exist.".format(id))
    return user



def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view