from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from flask_paginate import Pagination, get_page_args
from flaskr.auth import login_required
from flaskr.db import get_db
import time
from . import ESsearch

bp = Blueprint('question', __name__)

def get_posts(offset=0, per_page=12,posts=[]):
    return posts[offset: offset + per_page]

@bp.route('/')
def index():
    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')
    db=get_db()
    posts = db.execute(
        'SELECT *'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    total=len(posts)
    pagination_posts = get_posts(offset=offset, per_page=per_page,posts=posts)
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')
    return render_template('question/index.html',posts=pagination_posts,
                                                 page=page,
                                                 per_page=per_page,
                                                 pagination=pagination,)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        tag=request.form['tag']
        #print tag
        tags=tag.split(',')
        # s=string(tag)
        # print s
        error = None
        searchobj = ESsearch.ESearch()
        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (author_id,title,body)'
                ' VALUES (?, ?, ?)',
                ( g.user['id'],title, body)
            )
            x=db.execute( 'SELECT max(qid) as maximum FROM post').fetchone()
            data=db.execute("SELECT * FROM user WHERE id = ?", (g.user['id'],)).fetchone()
            lastid = int(x[0])
            tdata = db.execute("SELECT * from post where qid = ?",(lastid,)).fetchone()
            searchobj.insert(int(tdata[0]), int(tdata[1]), tdata[2], int(tdata[3]), tdata[4], tdata[5], tdata[6])
            
            flag=0
            if(data[5]>5) and tags is not None:
                for i in tags:
                        db.execute(
                            'INSERT INTO qtags (tagname,qid)'
                            ' VALUES (?, ?)',
                            (i,x[0])
                        )
                        r=db.execute("SELECT * FROM tags WHERE tagname = ?", (i,)).fetchone()
                        if(r is None):
                            db.execute(
                            'INSERT INTO tags (tagname)'
                            ' VALUES (?)',
                            (i,)
                            )
                            db.execute('INSERT INTO TagDescription (tagname)'
                            'VALUES (?)',
                            (i,))

            else:
                for i in tags:
                    data=db.execute("SELECT * FROM tags WHERE tagname = ?", (i,)).fetchone()
                    if(data is None):
                        flag=1
                        break
                    else:
                        continue
                if(flag==0):
                    for i in tags:
                        db.execute(
                            'INSERT INTO qtags (tagname,qid)'
                            ' VALUES (?, ?)',
                            (i,x[0])
                            )
                else:
                    print ("NO REPUTATION TO ADD TAGS")

            # print x['qid']
            #print x[0]
            
            db.commit()
            return redirect(url_for('question.index'))

    return render_template('question/create.html')

def get_question(id, check_author=True):
    post = get_db().execute(
        'SELECT qid, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE qid = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_question(id)
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None
        searchobj = ESsearch.ESearch()
        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE qid = ?',
                (title, body, id)
            )
            db.commit()
            lastid = int(id)
            tdata = db.execute("SELECT * from post where qid = ?",(lastid,)).fetchone()
            searchobj.insert(int(tdata[0]), int(tdata[1]), tdata[2], int(tdata[3]), tdata[4], tdata[5], tdata[6])
            
            return redirect(url_for('question.index'))

    return render_template('question/update.html', post=post)

@bp.route('/search', methods=('POST','GET'))
def search():
    print(request.method)
    if request.method == 'GET':
        page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')
        db=get_db()    
        pattern = request.args.get('tagname')
        print(pattern)
        if len(pattern)>0:
            newpat = str(pattern)
            tdata = db.execute("SELECT * from qtags where tagname = ?",(newpat,)).fetchall()
            posts = []
            for item in tdata:
                resp = db.execute(
                    'SELECT qid, title, body, created, author_id, username,profile_picture'
                    ' FROM post p JOIN user u ON p.author_id = u.id'
                    ' WHERE p.qid = ?', (int(item[1]),)
                ).fetchall()
                for items in resp:
                    posts.append(items)
                        
            total=len(posts)    
            pagination_posts = get_posts(offset=offset, per_page=per_page,posts=posts)
            pagination = Pagination(page=page, per_page=per_page, total=total,
                                    css_framework='bootstrap4')
            return render_template('question/index.html',posts=pagination_posts,
                                                        page=page,
                                                        per_page=per_page,
                                                        pagination=pagination,)
        else:
            return "Something wrong with the tag name!"

    if request.method == 'POST':

        page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')
        db=get_db()    
        pattern = request.form['pattern']
        if len(pattern)>0:
            if(pattern[0] == '[' and pattern[len(pattern)-1] == ']'):
                pattern = pattern[1:(len(pattern)-1)]
                newpat = ''.join(pattern)
                tdata = db.execute("SELECT * from qtags where tagname = ?",(newpat,)).fetchall()
                posts = []
                for item in tdata:
                    resp = db.execute(
                        'SELECT qid, title, body, created, author_id, username,profile_picture'
                        ' FROM post p JOIN user u ON p.author_id = u.id'
                        ' WHERE p.qid = ?', (int(item[1]),)
                    ).fetchall()
                    for items in resp:
                        posts.append(items)

            else:
                searchobj = ESsearch.ESearch()
                posts = searchobj.search(pattern)

            total=len(posts)    
            pagination_posts = get_posts(offset=offset, per_page=per_page,posts=posts)
            pagination = Pagination(page=page, per_page=per_page, total=total,
                                    css_framework='bootstrap4')
            return render_template('question/index.html',posts=pagination_posts,
                                                        page=page,
                                                        per_page=per_page,
                                                        pagination=pagination,)
        else:
            return "Please Enter Something to search!"

    else:
        return "something wrong happened!"

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    print("HI")
    get_question(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE qid = ?', (id,))
    db.commit()
    searchobj = ESsearch.ESearch()
    searchobj.delete(int(id))
    return redirect(url_for('question.index'))


@bp.route('/<int:id>/que',  methods=('GET','POST'))
def que(id):
    db = get_db()
    db = get_db()
    posts=db.execute('SELECT qid, title, body, created, author_id, username, upvotes,profile_picture'
        ' FROM post p JOIN user u ON p.author_id = u.id where qid =?' , (id,)).fetchone()
    tags=db.execute('SELECT * FROM qtags where qid=?',(id,)).fetchall()
    comments=db.execute('SELECT * FROM comment_question WHERE qid=?',(id,)).fetchall()
    ans=db.execute('SELECT * FROM answer a JOIN user u ON a.author_id=u.id WHERE qid = ? ORDER BY a.accepted DESC, upvotes DESC', (id,)).fetchall()
    ans_len=len(ans)
    comments_len=len(comments)
    tag_len=len(tags)
    list1={}
    tag_len=len(tags)
    for i in ans:
        # print "hello"
        # print i['id']
        # print "temp"
        ans4=db.execute('SELECT * FROM comment_answer WHERE ans_id=?',(i['id'],)).fetchall()
        # print len(ans4)
        list1[i['id']]=ans4
        # print  len(list1[i['id']])
    # comments_len_ans=len(ans1)
    return render_template('question/que.html',posts=posts,ans=ans,ans_len=ans_len,comments=comments,comments_len=comments_len,tags=tags,tag_len=tag_len,list1=list1)



@bp.route('/<int:id>/create_comment', methods=('GET', 'POST'))
@login_required
def create_comment(id):
    if request.method == 'POST':
        body = request.form['body']
        db = get_db()
        db.execute(
                'INSERT INTO comment_question(qid,author_id,body)'
                ' VALUES (?, ?, ?)',
                (id,g.user['id'], body)
            )
        db.commit()
        return redirect(url_for('question.que',id=id))

    return render_template('question/create_comment.html')


@bp.route('/<int:id>/upvote_question', methods=('GET', 'POST'))
@login_required
def upvote_question(id):
        db = get_db()
        result=db.execute('select * from upvote_que where qid=? and userid=?',(id,g.user['id'])).fetchone()
        if result is not None:
            if result[2]==2:
                db.execute('UPDATE upvote_que SET upvote_downvote=? WHERE qid = ? and userid=?',(1,id,g.user['id']))
                db.execute('UPDATE post SET upvotes= upvotes + 1 WHERE qid = ?',(id,))
        else:
            db.execute('insert into upvote_que(qid,userid,upvote_downvote) values(?,?,?)',(id,g.user['id'],1))          
            db.execute('UPDATE post SET upvotes=upvotes+1 WHERE qid = ?',(id,))
        db.commit()
        return redirect(url_for('question.que',id=id))


@bp.route('/<int:id>/downvote_question', methods=('GET', 'POST'))
@login_required
def downvote_question(id):
        db = get_db()
        result=db.execute('select * from upvote_que where qid=? and userid=?',(id,g.user['id'])).fetchone()
        if result is not None:
            if result[2]==1:
                db.execute('UPDATE upvote_que SET upvote_downvote=? WHERE qid = ? and userid=?',(2,id,g.user['id']))
                db.execute('UPDATE post SET upvotes=(upvotes-1) WHERE qid = ?',(id,))
        else:
            db.execute('insert into upvote_que(qid,userid,upvote_downvote) values(?,?,?)',(id,g.user['id'],2))
            db.execute('UPDATE post SET upvotes=(upvotes-1) WHERE qid = ?',(id,))    
        db.commit()
        return redirect(url_for('question.que',id=id)) 


@bp.route('/<int:id>/upvote_answer', methods=('GET', 'POST'))
@login_required
def upvote_answer(id):
        db = get_db()
        result=db.execute('select * from upvote_ans where id=? and userid=?',(id,g.user['id'])).fetchone()
        if result is not None:
            if result[2]==2:
                db.execute('UPDATE upvote_ans SET upvote_downvote=? WHERE id = ? and userid=?',(1,id,g.user['id']))
                db.execute('UPDATE answer SET upvotes= upvotes + 1 WHERE id = ?',(id,))
        else:
            db.execute('insert into upvote_ans(id,userid,upvote_downvote) values(?,?,?)',(id,g.user['id'],1))          
            db.execute('UPDATE answer SET upvotes=upvotes+1 WHERE id = ?',(id,))
        res=db.execute('select qid from answer where id=?',(id,)).fetchone()
        db.commit()
        return redirect(url_for('question.que',id=res['qid']))


@bp.route('/<int:id>/downvote_answer', methods=('GET', 'POST'))
@login_required
def downvote_answer(id):
        db = get_db()
        result=db.execute('select * from upvote_ans where id=? and userid=?',(id,g.user['id'])).fetchone()
        if result is not None:
            if result[2]==1:
                db.execute('UPDATE upvote_ans SET upvote_downvote=? WHERE id = ? and userid=?',(2,id,g.user['id']))
                db.execute('UPDATE answer SET upvotes=(upvotes-1) WHERE id = ?',(id,))
        else:
            db.execute('insert into upvote_ans(id,userid,upvote_downvote) values(?,?,?)',(id,g.user['id'],2))
            db.execute('UPDATE answer SET upvotes=(upvotes-1) WHERE id = ?',(id,))    
        db.commit()
        res=db.execute('select qid from answer where id=?',(id,)).fetchone()
        return redirect(url_for('question.que',id=res['qid'])) 


@bp.route('/<int:id>/createanswer', methods=('GET', 'POST'))
@login_required
def createanswer(id):
    if request.method == 'POST':
        body = request.form['body']
        db = get_db()
        db.execute(
            'INSERT INTO answer (qid,author_id,body)'
            ' VALUES (?, ?, ?)',
            (id, g.user['id'], body)
        )
        db.execute(
            'UPDATE user SET reputation =reputation+1 '
            ' WHERE id = ?',
            (g.user['id'],)
        )        
        db.commit()
        return redirect(url_for("question.que", id=id))

    return render_template('question/createanswer.html')

@bp.route('/<int:qid>/<int:aid>/create_comment_ans', methods=('GET', 'POST'))
@login_required
def create_comment_ans(qid,aid):
    if request.method == 'POST':
        body = request.form['body']
        db = get_db()
        db.execute(
                'INSERT INTO comment_answer(ans_id,author_id,body)'
                ' VALUES (?, ?, ?)',
                (aid,g.user['id'], body)
                 )
        db.commit()
        return redirect(url_for('question.que',id=qid))

    return render_template('question/create_comment_ans.html')

def get_answer(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, qid, body, created, author_id, username'
        ' FROM answer p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@bp.route('/<int:id>/updateanswer', methods=('GET', 'POST'))
@login_required
def updateanswer(id):
    post = get_answer(id)

    if request.method == 'POST':
        body = request.form['body']
        db = get_db()
        db.execute(
            'UPDATE answer SET body = ?'
            ' WHERE id = ?',
            (body, id)
        )
        db.commit()
        return redirect(url_for('question.que', id=post['qid']))

    return render_template('question/updateanswer.html', post=post)

@bp.route('/<int:id>/deleteanswer', methods=('POST',))
@login_required
def deleteanswer(id):
    print (id)
    q = get_answer(id)
    db = get_db()
    db.execute('DELETE FROM answer WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('question.que', id=q['qid']))

@bp.route('/<int:qid>/<int:aid>/accept_answer', methods=('GET', 'POST'))
@login_required
def accept_answer(aid, qid):
        db = get_db()
        result=db.execute('select * from post where qid=? and author_id=?',(qid,g.user['id'])).fetchone()
        res = db.execute('select * from answer where id =?',(aid,)).fetchone()
        if result is not None  and result['accepted']!=1 and res['author_id']!=g.user['id']:
            db.execute('UPDATE user SET reputation= reputation + 5 where id =?',(res['author_id'],))
            db.execute('UPDATE post SET accepted =1 where qid =?',(qid,))
            db.execute('UPDATE answer SET accepted= 1 WHERE id = ?',(aid,))
        res=db.execute('select qid from answer where id=?',(aid,)).fetchone()
        db.commit()
        return redirect(url_for('question.que',id=res['qid']))

@bp.route('/about', methods=('POSTS','GET'))
def about():
    return render_template("question/about.html")

@bp.errorhandler(404)
def page_not_found(e):
    return render_template('auth/404.html'), 404