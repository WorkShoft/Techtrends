import datetime
import logging
import sqlite3
import sys

from flask import Flask, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort


# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection


# Function to get a post using its ID
def get_post(post_id):
    update_query_statistics()
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                              (post_id,)).fetchone()
    connection.close()

    if post:
        app.logger.info("Article %s retrieved!", post[2])
    return post


def update_query_statistics():
    connection = get_db_connection()
    connection.execute("INSERT INTO query_statistics DEFAULT VALUES")
    connection.commit()
    connection.close()


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hgfu983ru6587yt10fjw83ft94847-3h4rgjh3yg490hg3745g4hr87gh5-276hg-9'


# Define the main route of the web application
@app.route('/')
def index():
    update_query_statistics()
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)


# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    update_query_statistics()
    post = get_post(post_id)
    if post is None:
        app.logger.info("Article Not Found")
        return render_template('404.html'), 404
    else:
        return render_template('post.html', post=post)


# Define the About Us page
@app.route('/about')
def about():
    app.logger.info("Accessed About Us")
    return render_template('about.html')


@app.route('/healthz')
def healthz():
    return json.dumps({"result": "OK - healthy"})


@app.route('/metrics')
def metrics():
    update_query_statistics()
    connection = get_db_connection()
    post_count = connection.execute('SELECT COUNT(*) FROM posts').fetchone()
    db_connection_count = connection.execute('SELECT COUNT(*) FROM query_statistics').fetchone()
    connection.close()
    return json.dumps({"db_connection_count": db_connection_count[0], "post_count": post_count[0], })


# Define the post creation functionality
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            update_query_statistics()
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                               (title, content))
            connection.commit()
            connection.close()

            app.logger.info("Created article '%s'", title)
            return redirect(url_for('index'))

    return render_template('create.html')


# start the application on port 3111
if __name__ == "__main__":
    app.run(host='0.0.0.0', port='3111', debug=True)

    logging.basicConfig(level=logging.DEBUG)
