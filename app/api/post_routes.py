from flask import Blueprint, request, jsonify
from app.models import db, Post, Comment, User
from app.forms import PostForm, CommentForm
from datetime import datetime
from flask_login import login_required, current_user
from app.aws_s3 import (
    upload_file_to_s3, allowed_file, get_unique_filename)


post_routes = Blueprint('posts', __name__)

def validation_errors_to_error_messages(validation_errors):
    errorMessages = []
    for field in validation_errors:
        for error in validation_errors[field]:
            errorMessages.append(f'{error}')
    return errorMessages


# Get all Posts
@post_routes.route('/myfeed')
def posts():
    posts = Post.query.all()
    data = [post.to_dict() for post in posts]
    return {'posts': data}

# Create a Post

@post_routes.route('/newpost', methods=['POST'])
def newpost():
    form = PostForm()
    form['csrf_token'].data = request.cookies['csrf_token']

    if "photo" not in request.files:
        return {"errors": "image required"}, 400

    photo = request.files["photo"]


    if not allowed_file(photo.filename):
        return {"errors": "file type not permitted"}, 400

    photo.filename = get_unique_filename(photo.filename)

    upload = upload_file_to_s3(photo)

    if "url" not in upload:
        # if the dictionary doesn't have a url key
        # it means that there was an error when we tried to upload
        # so we send back that error message
        return upload, 400

    url = upload["url"]
    # flask_login allows us to get the current user from the request
    # new_image = Image(user=current_user, url=url)


    if form.validate_on_submit():
        new_post = Post(
            user_id = form.data['user_id'],
            photo = url,
            caption = form.data['caption'],
            location = form.data['location']
        )
        db.session.add(new_post)
        db.session.commit()

        return new_post.to_dict()

    return {'errors': validation_errors_to_error_messages(form.errors)}, 400

# Get a Single Post (when on a profile Page, this will be a modal)

# Update a Post

@post_routes.route('/<id>', methods=['PUT'])
def updatepost(id):
    form = PostForm()

    form['csrf_token'].data = request.cookies['csrf_token']
    post = Post.query.get(id)


    if form.validate_on_submit():
        # post.photo = form.data['photo']
        post.caption = form.data['caption']
        post.location = form.data['location']

        db.session.commit()
        return post.to_dict()
    return {'errors': validation_errors_to_error_messages(form.errors)}, 400

# Delete a Post

@post_routes.route('/<id>', methods=['DELETE'])
def deletepost(id):
    post = Post.query.get(id)

    db.session.delete(post)
    db.session.commit()
    return post.to_dict()

# Leave and remove a like on a Post
@post_routes.route('/<id>/like', methods=['POST'])
def post_like(id):
    post = Post.query.get(id)

    if current_user in post.post_likes:
        post.post_likes.remove(current_user)
        db.session.add(post)
        db.session.commit()
        return post.to_dict()

    post.post_likes.append(current_user)

    db.session.add(post)
    db.session.commit()
    return post.to_dict()
