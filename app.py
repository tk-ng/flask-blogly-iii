"""Blogly application."""

from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask, request, redirect, render_template, url_for
from models import db, connect_db, User, Post, Tag, PostTag, default_img_url

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)
db.create_all()


app.config['SECRET_KEY'] = "SECRET"
debug = DebugToolbarExtension(app)


@app.route('/')
def home_page():
    posts = Post.query.limit(5).all()
    return render_template('home.html', posts=posts)


@app.errorhandler(404)
def page_not_found():
    return render_template('404.html'), 404


@app.route('/users')
def all_users():
    """Home page that shows a list of all users. With a 'Add user' button."""
    users = User.query.order_by(User.last_name, User.first_name).all()
    return render_template("users.html", users=users)


@app.route('/users/new', methods=["GET", "POST"])
def create_user():
    """Show or submit the create a user form."""
    if request.method == 'POST':
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        img_url = request.form["img_url"] or None
        # if not (img_url):
        #     img_url = None
        new_user = User(first_name=first_name,
                        last_name=last_name, image_url=img_url)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('all_users'))
    else:
        return render_template("add_user.html")


@app.route("/users/<int:user_id>")
def show_user_detail(user_id):
    """Show details about a single user."""
    user = User.query.get_or_404(user_id)
    posts = user.posts
    return render_template("user_detail.html", user=user, posts=posts)


@app.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
def edit_user_detail(user_id):
    """Show or save the edited details of a single user."""
    if request.method == 'POST':
        user = User.query.get_or_404(user_id)
        user.first_name = request.form["first_name"]
        user.last_name = request.form["last_name"]
        user.image_url = request.form["img_url"] or None
        if not (request.form["img_url"]):
            user.image_url = default_img_url
        db.session.commit()
        return redirect(url_for('all_users'))
    else:
        user = User.query.get_or_404(user_id)
        return render_template("user_edit.html", user=user)


@app.route("/users/<int:user_id>/delete", methods=["POST"])
def delete_user_from_db(user_id):
    """Delete a single user from the database."""
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect("/users")


@app.route('/users/<int:user_id>/posts/new', methods=["GET", "POST"])
def add_post(user_id):
    """Show create new post form OR Create a new post by the user."""
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        title = request.form["title"]
        content = request.form["content"]
        tags = [Tag.query.filter_by(name=n).one()
                for n in request.form.getlist('post-tags')]
        new_post = Post(title=title, content=content,
                        user_id=user_id, tags=tags)
        db.session.add(new_post)
        db.session.commit()
        return redirect(f"/users/{user_id}")
    else:
        tags = Tag.query.all()
        return render_template("add_post.html", user=user, tags=tags)


@app.route('/posts/<int:post_id>')
def show_post(post_id):
    post = Post.query.get(post_id)
    return render_template('post_detail.html', post=post)


@app.route('/posts/<int:post_id>/edit', methods=["GET", "POST"])
def save_post_Edit(post_id):
    if request.method == 'POST':
        post = Post.query.get_or_404(post_id)
        post.title = request.form["title"]
        post.content = request.form["content"]
        post.tags = [Tag.query.filter_by(name=n).one()
                     for n in request.form.getlist('post-tags')]
        db.session.commit()
        return redirect(url_for('show_post', post_id=post.id))
    else:
        post = Post.query.get(post_id)
        tags = Tag.query.all()
        return render_template('post_edit.html', post=post, tags=tags)


@app.route("/posts/<int:post_id>/delete", methods=["POST"])
def delete_post_from_db(post_id):
    """Delete a single post from the database."""
    post = Post.query.get_or_404(post_id)
    user_id = post.user.id
    db.session.delete(post)
    db.session.commit()
    return redirect(f"/users/{user_id}")


@app.route("/tags")
def list_tags():
    tags = Tag.query.all()
    return render_template("tags.html", tags=tags)


@app.route("/tags/<int:tag_id>")
def show_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    posts = tag.posts
    return render_template("tag_detail.html", tag=tag, posts=posts)


@app.route("/tags/new", methods=["GET", "POST"])
def add_tag():
    if request.method == 'POST':
        name = request.form["name"]
        new_tag = Tag(name=name)
        db.session.add(new_tag)
        db.session.commit()
        return redirect(url_for("list_tags"))
    else:
        return render_template("add_tag.html")


@app.route("/tags/<int:tag_id>/edit", methods=["GET", "POST"])
def edit_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    if request.method == 'POST':
        tag.name = request.form["name"]
        db.session.commit()
        return redirect(url_for('list_tags'))
    else:
        return render_template("tag_edit.html", tag=tag)


@app.route("/tags/<int:tag_id>/delete", methods=["POST"])
def delete_tag(tag_id):
    tag = Tag.query.get(tag_id)
    db.session.delete(tag)
    db.session.commit()
    return redirect(url_for('list_tags'))
