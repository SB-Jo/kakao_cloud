from flask import Flask, flash, jsonify, send_file, Blueprint
from flask import request, redirect, render_template, session
from forms import RegisterForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from models import db
from kakao_analyze import read_file, tokenize, get_count
from io import BytesIO, StringIO
import os

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET', 'POST'])
def home():
    userid = session.get('userid', None)
    if request.method == 'POST':
        f = request.files['file']
        filename = f.filename
        f.save('kakao.txt')
        talk_dic = read_file('kakao.txt')
        db.kakao.insert_one({'userid':userid,
                            'filename':filename,
                            'talk_set':talk_dic})
        os.remove('kakao.txt')
        return redirect('/')
    files = list(db.kakao.find({'userid':userid}))
    return render_template('home.html', userid=userid, files=files)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = db.users.find_one({'id':form.data.get('userid')})
        error = None
        if not user:
            error = '존재하지 않는 사용자입니다.'
        elif not check_password_hash(user.get('password'), form.data.get('password')):
            error = '비밀번호가 올바르지 않습니다.'
        if error is None:
            session.clear()
            session['userid'] = form.data.get('userid')
            return redirect('/')
        flash(error)
    return render_template('login.html', form=form)

@bp.route('/logout', methods=['GET'])
def logout():
    session.pop('userid', None)
    return redirect('/')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user_id = form.data.get('userid')
        user_password = generate_password_hash(form.data.get('password'))
        db.users.insert_one({'id':user_id,'password':user_password})
        return redirect('/login')
    return render_template('register.html', form=form)

@bp.route('/wc/<filename>', methods=['GET'])
def word_count(filename):
    userid = session.get('userid', None)
    if not userid:
        return render_template('/login')
    file = db.kakao.find_one({'filename':filename})
    talks  = file['talk_set']
    talk_set = {}
    for talker, talks in talks.items():
        talk_set[talker] = talks
    tokenized_talk = tokenize(talk_set)
#    db.tokenized.insert_one({'filename':filename,
#                            'tokenized':tokenized_talk})
    wcs = get_count(tokenized_talk)
    talkers = [talker for talker in tokenized_talk.keys()]

    return render_template('wcs.html', talkers=talkers, wcs=wcs)

        
@bp.route('/delete', methods=['POST'])
def delete_file():
    userid = session.get('userid', None)
    if not userid:
        return render_template('login.html')

    data = request.get_json()
    file_name = data.get('file_name')
    file = db.kakao.find_one({'filename':file_name})
    talkers = [talker for talker in file['talk_set'].keys()]
    for talker in talkers:
        os.remove(f"./static/wordcloud_{talker}.png")
    db.kakao.delete_many({'filename':file_name})
    return jsonify()