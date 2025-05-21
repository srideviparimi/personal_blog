from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash,request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text,ForeignKey
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from forms import CreatePostForm,RegisterForm,LoginForm,CommentForm,ContactForm
from typing import List

'''
On Windows type:
python -m pip install -r requirements.txt
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap5(app)
# TODO: Configure Flask-Login
login_manager=LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User,user_id)


# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db?timeout=10'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLES
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped["User"] = relationship(back_populates="posts")
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

# TODO: Create a User table for all your registered users.
class User(UserMixin,db.Model):
    __tablename__="user"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    name:Mapped[str]=mapped_column(String(1000),nullable=False)
    email:Mapped[str]=mapped_column(String(250),nullable=False,unique=True)
    password:Mapped[str]=mapped_column(String(100),nullable=False)
    posts:Mapped[List["BlogPost"]]=relationship(back_populates="author")
    comments:Mapped[List["Comment"]]=relationship(back_populates="comment_author")

class Comment(UserMixin,db.Model):
    __tablename__="comment"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    author_id:Mapped[int]=mapped_column(Integer, ForeignKey("user.id"))
    comment_author:Mapped["User"]=relationship(back_populates="comments")
    body:Mapped[str]=mapped_column(String(1000),nullable=True)

class Contact(UserMixin,db.Model):
    __tablename__="contact"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    name:Mapped[str]=mapped_column(String(1000),nullable=False)
    email:Mapped[str]=mapped_column(String(150),nullable=False)
    message:Mapped[str]=mapped_column(String(2000),nullable=False)
    phone:Mapped[str]=mapped_column(String(20),nullable=False)
'''
with app.app_context():
    db.create_all()
'''
# TODO: Use Werkzeug to hash the user's password when creating a new user.
@app.route('/register',methods=["GET","POST"])
def register():
    register_form=RegisterForm()
    if register_form.validate_on_submit():
        text_password=request.form.get('password')
        hash_password=generate_password_hash(text_password,method='pbkdf2',salt_length=8)
        new_user=User(
            name=request.form.get('name'),
            email=request.form.get('email'),
            password=hash_password
        )
        try:
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('get_all_posts'))
        except IntegrityError as e:
            flash("Your email already exists. Please login or use another one to register")
            return redirect(url_for('register'))

    return render_template("register.html",form=register_form)


# TODO: Retrieve a user from the database based on their email. 
@app.route('/login',methods=["GET","POST"])
def login():
    login_form=LoginForm()
    if login_form.validate_on_submit():
        email_id=request.form.get("email")
        password=request.form.get("password")
        resp = db.session.query(User).where(User.email == email_id)
        user_in_db = resp.scalar()
        if  user_in_db and check_password_hash(user_in_db.password,password):
            login_user(user_in_db)
            return redirect(url_for('get_all_posts'))
        else:
            flash("Email or Password not found.")
            return redirect(url_for('login'))
    return render_template("login.html",form=login_form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts)

def get_comments():
    res = db.session.execute(db.select(Comment))
    comments = res.scalars().all()
    return comments
# TODO: Allow logged-in users to comment on posts
@app.route("/post/<int:post_id>",methods=["GET","POST"])
@login_required
def show_post(post_id):

    requested_post = db.get_or_404(BlogPost, post_id)
    comment_form=CommentForm()
    comments=get_comments()
    if comment_form.validate_on_submit():
        new_comment=Comment(
            author_id=current_user.id,
            comment_author=current_user,
            body=comment_form.body.data
        )
        db.session.add(new_comment)
        db.session.commit()
        comments=get_comments()
        return redirect(url_for('show_post',post_id=post_id,comments=comments))

    return render_template("post.html", post=requested_post,form=comment_form,comments=comments)


# TODO: Use a decorator so only an admin user can create a new post
def admin_only(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if current_user.id!=1:
            abort(403)
        return f(*args,**kwargs)
    return decorated_function

@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


# TODO: Use a decorator so only an admin user can edit a post
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )

    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)


# TODO: Use a decorator so only an admin user can delete a post
@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact",methods=["GET","POST"])
@login_required
def contact():
    contact_form=ContactForm()
    if contact_form.validate_on_submit():
        name=contact_form.name.data
        email=contact_form.email.data
        phone=contact_form.phone.data
        message=contact_form.message.data
        new_contact=Contact(
            name=name,
            email=email,
            phone=phone,
            message=message
        )
        db.session.add(new_contact)
        db.session.commit()
        flash("Thank you for contacting us.")
        return redirect(url_for('contact'))


    return render_template("contact.html",form=contact_form)


if __name__ == "__main__":
    app.run(debug=True)
