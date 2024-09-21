"""Models for Blogly."""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


def connect_db(app):
    db.app = app
    db.init_app(app)


default_img_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTfkliTdTUC5h-3HTHn7-BWh02eYjlrobu_dw&s"


class User(db.Model):
    """ User."""

    __tablename__ = "users"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)

    first_name = db.Column(db.Text,
                           nullable=False)

    last_name = db.Column(db.Text,
                          nullable=False)

    image_url = db.Column(db.Text,
                          nullable=False,
                          default=default_img_url)

    posts = db.relationship("Post", backref="user",  # https://www.geeksforgeeks.org/sqlalchemy-cascading-deletes/#
                            cascade="all, delete")

    def __repr__(self):
        """Show info about user."""
        u = self
        return f"<User first_name={u.first_name} last_name={u.last_name} image_url={u.image_url}>"

    @property
    def full_name(self):
        """return the full name."""
        return f"{self.first_name} {self.last_name}"

    # def get_full_name(self):
    #     """return the full name."""
    #     return f"{self.first_name} {self.last_name}"

    # full_name = property(
    #     fget=get_full_name
    # )


class Post(db.Model):
    """Posts."""

    __tablename__ = "posts"

    id = db.Column(db.Integer,
                   primary_key=True)

    title = db.Column(db.Text,
                      nullable=False)

    content = db.Column(db.Text,
                        nullable=False)

    created_at = db.Column(db.DateTime,
                           default=datetime.now)

    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id'))

    @property
    def created_time(self):
        d = self.created_at
        return d.strftime("%a %b %d %Y, %I:%M %p")


class Tag(db.Model):
    """Tags."""

    __tablename__ = "tags"

    id = db.Column(db.Integer,
                   primary_key=True)
    name = db.Column(db.Text,
                     nullable=False,
                     unique=True)

    posts = db.relationship("Post",
                            secondary="posts_tags",
                            cascade="all,delete",
                            backref="tags")


class PostTag(db.Model):
    """Join table of Post and Tag."""

    __tablename__ = "posts_tags"

    post_id = db.Column(db.Integer,
                        db.ForeignKey('posts.id'),
                        primary_key=True,)

    tag_id = db.Column(db.Integer,
                       db.ForeignKey('tags.id'),
                       primary_key=True)
