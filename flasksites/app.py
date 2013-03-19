#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import request
from flask import session
from flask import redirect
from flask import url_for
from flask import abort
from flask import render_template
from flask import flash
from flask import g
from flask.ext.paginate import Pagination
from sqlalchemy import or_

from settings import db
from settings import app
from models import User
from models import Site
from models import Tag
from utils import get_or_create_tag
from utils import thumbnail_filter
from utils import shorter_url_filter
from utils import format_datetime_filter

app.jinja_env.filters['thumbnail'] = thumbnail_filter
app.jinja_env.filters['shorter_url'] = shorter_url_filter
app.jinja_env.filters['format_datetime'] = format_datetime_filter


@app.before_request
def before_request():
    g.user = User.query.filter_by(id=session.get('user_id')).first()


@app.route('/account/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password != confirm_password:
            error = 'confirm password'
        else:
            user = User(username, email, password)
            db.session.add(user)
            db.session.commit()
            flash('Signup successfully')
            return redirect(url_for('login'))
    else:
        return render_template('register.html', error=error)


@app.route('/account/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email, password=password).first()
        if user is None:
            error = 'Invalid email or password'
        else:
            session['logged_in'] = True
            session['user_id'] = user.id
            flash('You were logged in')
            return redirect('/')
    return render_template('login.html', error=error)


@app.route('/add', methods=['GET', 'POST'])
def add_site():
    if not session.get('logged_in'):
        abort(401)

    user = User.query.filter_by(id=session.get('id')).first()
    error = None
    if request.method == 'POST':
        title = request.form.get('title', '')
        website = request.form.get('url', '')
        description = request.form.get('description', '')
        source_url = request.form.get('source_url', '')
        tags_names = request.form.get('tags', '').split(',')
        tags_names = filter(lambda s: s, [tag.strip() for tag in tags_names])

        site = Site.query.filter_by(website=website).first()
        if site is None:
            # Add site info to db
            site = Site(title=title, website=website, description=description,
                        source_url=source_url, submitted_by=user)
            for tag in map(get_or_create_tag, tags_names):
                site.tags.append(tag)
            db.session.add(site)
            db.session.commit()
            flash('New site was successfully added!')

        return redirect(url_for('show_site', site_id=site.id))
    else:
        return render_template('add_site.html', error=None)


@app.route('/')
@app.route('/sites/')
def all_sites(mine=False, username=None, keyword=None,
              tag_name=None, opensource=False):
    sites = None

    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    if mine:
        user = User.query.filter_by(id=session.get('id')).first()
        query = Site.query.filter_by(submitted_by=user)
    elif username:
        author = User.query.filter_by(username=username).first()
        sites = author.sites
    elif keyword:
        tags = Tag.query.filter(Tag.name.like('%' + keyword + '%')).all()

        # http://www.mail-archive.com/sqlalchemy@googlegroups.com/msg18662.html
        query = Site.query.filter(or_(Site.title.like('%' + keyword + '%'),
                                      Site.description.like('%' + keyword
                                      + '%'),
                                      Site.tags.any(Tag.id.in_(
                                                    [tag.id for tag in tags]
                                                    ))
                                      ))
        # query2 = Site.query.join(Site.tags)\
                     # .filter(Tag.id.in_([tag.id for tag in tags]))

        # site1 = query.order_by(Site.submitted_at.desc())
        # site2 = query2.order_by(Site.submitted_at.desc())
        # sites = site1 + site2
        # count = len(sites)

        # print sites
    elif tag_name:
        tag = Tag.query.filter_by(name=tag_name).first()
        sites = tag.sites
    elif opensource:
        query = Site.query.filter(Site.source_url != '')
    else:
        query = Site.query

    if sites is None:
        sites = query.order_by(Site.submitted_at.desc())

    pagination = Pagination(page=page, total=sites.count(), per_page=6)
    sites = sites.paginate(page, per_page=6, error_out=False)

    return render_template('index.html', sites=sites, pagination=pagination,
                           keyword=keyword, mine=mine, tag_name=tag_name,
                           opensource=opensource, username=username)


@app.route('/mine/')
def mine():
    if not session.get('logged_in'):
        abort(401)
    else:
        return all_sites(mine=True)


@app.route('/search/')
def search():
    keyword = request.args.get('q')
    if not keyword:
        return redirect('/')
    else:
        return all_sites(keyword=keyword)


@app.route('/tagged/<tag_name>/')
def tagged(tag_name):
    return all_sites(tag_name=tag_name)


@app.route('/by/<username>/')
def submitted_by(username):
    return all_sites(username=username)


@app.route('/opensource/')
def opensource():
    return all_sites(opensource=True)


@app.route('/site/<int:site_id>')
def show_site(site_id):
    site = Site.query.filter_by(id=site_id).first()
    return render_template('detail.html', site=site)


@app.route('/tags')
def all_tags():
    tags = Tag.query.all()
    return render_template('tags.html', tags=tags)


# @app.route('/account')
# def account():
    # user = session.get('user')
    # return render_template('account.html', user)
@app.route('/account/settings', methods=['GET', 'POST'])
def preference():
    if not session.get('logged_in'):
        abort(401)
    user = User.query.filter_by(id=session.get('user_id')).first()

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not all((email, password)):
            flash('error')
        elif confirm_password and confirm_password != password:
            flash('error')
        else:
            if email != user.email:
                if User.query.filter_by(email=email).first() is not None:
                    flash('error')
                else:
                    user.email = email
            user.password = password
            db.session.add(user)
            db.session.commit()
            flash('Update successfully!')
    return render_template('settings.html', user=user)


@app.route('/account/logout')
def logout():
    session.pop('logged_in', None)
    del g.user
    flash('You were logged out')
    return redirect('/')

if __name__ == '__main__':
    app.run()
