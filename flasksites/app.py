#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import request, session, redirect, url_for, abort
from flask import render_template, flash, g

from flask.ext.paginate import Pagination
from flask.ext.login import LoginManager, login_required, login_user
from flask.ext.login import logout_user, current_user
from sqlalchemy import or_

from settings import db, app
from models import User, Site, Tag
from utils import get_or_create_tag, thumbnail_filter, shorter_url_filter
from utils import format_datetime_filter, create_user, set_password
from utils import auth_user

app.jinja_env.filters['thumbnail'] = thumbnail_filter
app.jinja_env.filters['shorter_url'] = shorter_url_filter
app.jinja_env.filters['format_datetime'] = format_datetime_filter
login_manager = LoginManager()
login_manager.setup_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# @app.before_request
# def before_request():
    # g.user = User.query.filter_by(id=session.get('user_id')).first()


@app.route('/account/register', methods=['GET', 'POST'])
def register():
    error = None

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not all([username, email, password, confirm_password]):
            error = 'All label is required!'
        elif password != confirm_password:
            error = 'Please confirm password! '
        else:
            create_user(username, email, password)
            flash('Signup successfully')
            return redirect(url_for('login'))
    return render_template('register.html', error=error)


@app.route('/account/login', methods=['GET', 'POST'])
def login():
    error = None
    next_url = request.args.get('next', url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', "no") == "yes"

        if not all([email, password]):
            error = 'Email and password is required!'
        else:
            user = auth_user(email, password)
            if user is None:
                error = 'Invalid email or password!'
            else:
                if login_user(user, remember=remember):
                    flash('Logged in successfully.')
                    return redirect(next_url)
    return render_template('login.html', error=error)


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_site():
    error = None
    if request.method == 'POST':
        title = request.form.get('title', '')
        website = request.form.get('url', '')
        description = request.form.get('description', '')
        source_url = request.form.get('source_url', '')
        tags_names = request.form.get('tags', '').split(',')
        tags_names = filter(lambda s: s, [tag.strip() for tag in tags_names])

        if not website:
            error = 'Site URL is required!'
        else:
            site = Site.query.filter_by(website=website).first()
            if site is None:
                # Add site info to db
                site = Site(title=title, website=website,
                            description=description,
                            source_url=source_url, submitted_by=current_user)
                for tag in map(get_or_create_tag, tags_names):
                    site.tags.append(tag)
                db.session.add(site)
                db.session.commit()
                # flash('New site was successfully added!')
            return redirect(url_for('show_site', site_id=site.id))
    return render_template('add_site.html', error=error)


@app.route('/')
@app.route('/sites/')
def index(mine=False, username=None, keyword=None,
          tag_name=None, opensource=False):
    sites = None

    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    if mine:
        query = Site.query.filter_by(submitted_by=current_user)
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
@login_required
def mine():
    return index(mine=True)


@app.route('/search/')
def search():
    keyword = request.args.get('q')
    if not keyword:
        return redirect('/')
    else:
        return index(keyword=keyword)


@app.route('/tagged/<tag_name>/')
def tagged(tag_name):
    return index(tag_name=tag_name)


@app.route('/by/<username>/')
def submitted_by(username):
    return index(username=username)


@app.route('/opensource/')
def opensource():
    return index(opensource=True)


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
@login_required
def settings():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not email:
            flash('Email address is required!')
        else:
            if email != current_user.email:
                if User.query.filter_by(email=email).first() is not None:
                    flash('Email address already exists!')
                else:
                    current_user.email = email
                    db.session.add(current_user)
                    db.session.commit()
                    flash('Email address update successfully!')

        if confirm_password and confirm_password != password:
            flash('Please confirm password!')
        else:
            set_password(current_user, password)
            flash('Password update successfully!')
    return render_template('settings.html', user=current_user)


@app.route('/account/logout')
@login_required
def logout():
    logout_user()
    flash('You were logged out!')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
