from flask import Flask, flash, redirect, request, url_for, render_template, make_response, get_flashed_messages
import logging
from logging.handlers import RotatingFileHandler
import os
from user_repository import UserRepository
from validator import validate_user_data

app = Flask(__name__)
app.secret_key = "secret_key"


def setup_logging():
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10240,
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.DEBUG)

    app.logger.addHandler(file_handler)
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.DEBUG)
    app.logger.info('Application startup')

setup_logging()


@app.route("/")
def index():
    app.logger.debug('Main page accessed')
    return render_template('index.html')

@app.get('/users/')
def users_index():
    query = request.args.get('query')
    app.logger.debug(f'Searching users with query: {query}')
    
    repo = UserRepository()
    users = repo.get_content()
    if query:
        filtered_users = list(filter(lambda user: query.lower() in user['name'].lower(), users))
        app.logger.debug(f'Found {len(filtered_users)} matching users')
    else:
        query = ''
        filtered_users = users
        app.logger.debug('No search query, showing all users')
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        "users/index.html",
        users=filtered_users,
        search=query,
        messages=messages,
    )


@app.get('/users/<id>')
def users_show(id):
    repo = UserRepository()
    user = repo.find(id)
    
    return render_template(
        'users/show.html',
        user=user,
    )


@app.get('/users/new')
def users_new():
    app.logger.debug('Rendering new user form')
    user = {'name': '', 'email': ''}
    errors = []
    return render_template(
        "users/new.html",
        user=user,
        errors=errors,
        )


@app.post('/users')
def users_post():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    app.logger.debug(f'Attempting to add new user: {name}, {email}')
    
    repo = UserRepository()
    errors = validate_user_data(name, email, repo)
    
    if errors:
        app.logger.warning(f'Validation errors: {errors}')
        return render_template(
            "users/new.html",
            user={'name': name, 'email': email},
            errors=errors,
        ), 422
    
    new_user = {
        'name': name,
        'email': email
    }
    
    try:
        user_id = repo.save(new_user)
        app.logger.info(f'Successfully added new user with ID: {user_id}')
        flash("Пользователь успешно добавлен", "success")
        return redirect(url_for('users_index'))
    except Exception as e:
        app.logger.error(f'Failed to save user: {str(e)}')
        flash("Ошибка при сохранении пользователя", "error")
        return render_template(
            "users/new.html",
            user={'name': name, 'email': email},
            errors=["Ошибка при сохранении данных"],
        ), 500


@app.get("/users/<id>/edit")
def users_edit(id):
    repo = UserRepository()
    user = repo.find(id)
    errors = []

    return render_template(
        "users/edit.html",
        user=user,
        errors=errors,
    )


@app.route("/users/<id>/patch", methods=["POST"])
def users_patch(id):
    repo = UserRepository()
    user = repo.find(id)
    
    data = request.form.to_dict()
    name = data['name']
    email = data['email']
    
    errors = validate_user_data(name, email, repo, update=True)
    if errors:
        return render_template(
            "users/edit.html",
            user=user,
            errors=errors,
        ), 422

    user["name"] = name
    user["email"] = email
    repo.save(user)
    flash("User has been updated", "success")
    return redirect(url_for("users_index"))


if __name__ == '__main__':
    app.run(debug=True)