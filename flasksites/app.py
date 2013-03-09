#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import request
from flask import session
from flask import g
from flask import redirect
from flask import url_for
from flask import abort
from flask import render_template
from flask import flash

from settings import db
from settings import app
from models import User


def init_db():
    db.create_all()


@app.route('/register', methods=['GET', 'POST'])
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


@app.route('/login', methods=['GET', 'POST'])
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
            session['username'] = user.username
            flash('You were logged in')
            return redirect('/')
    return render_template('login.html', error=error)


@app.route('/add', methods=['GET', 'POST'])
def add_site():
    if not session.get('logged_in'):
        abort(401)

    error = None
    if request.method == 'POST':
        title = request.form.get('title', '')
        url = request.form.get('url', '')
        description = request.form.get('description', '')
        source_url = request.form.get('source_url', '')
        tags = request.form.get('tags', '')

        flash('New site was successfully added')
        return redirect(url_for('show_sites'))
    else:
        return render_template('add_site.html', error=None)


@app.route('/')
@app.route('/sites/')
def show_sites():
    sites = []
    return render_template('index.html', sites=sites)


@app.route('/sites/mine/')
def show_mine_sites():
    if not session.get('logged_in'):
        abort(401)

    sites = []
    return render_template('show_sites.html', sites=sites)


@app.route('/sites/search/')
def search_sites():
    keyword = request.args.get('q')
    if not keyword:
        return redirect('/')
    sites = []
    return render_template('show_sites.html', sites=sites, keyword=keyword)


@app.route('/site/<int:site_id>')
def show_site(site_id):
    sites = []
    return render_template('site.html', site=site)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_sites'))

if __name__ == '__main__':
    app.run()
