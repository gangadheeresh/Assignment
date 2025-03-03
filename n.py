from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    followers = db.relationship('Follow', foreign_keys='Follow.followed_id', backref='followed', lazy=True)
    following = db.relationship('Follow', foreign_keys='Follow.follower_id', backref='follower', lazy=True)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment', backref='post', lazy=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user = db.relationship('User', backref='comments')

class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        posts = Post.query.order_by(Post.id.desc()).all()
        return render_template('BB.html', user=user, posts=posts)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    return render_template('CC.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('index'))
        flash('Invalid username or password.')
    return render_template('DD.html')

@app.route('/logout')
def logout():  # Ensure this route is defined
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/post', methods=['POST'])
def create_post():
    if 'user_id' in session:
        content = request.form['content']
        new_post = Post(content=content, user_id=session['user_id'])
        db.session.add(new_post)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/comment/<int:post_id>', methods=['POST'])
def create_comment(post_id):
    if 'user_id' in session:
        content = request.form['content']
        new_comment = Comment(content=content, user_id=session['user_id'], post_id=post_id)
        db.session.add(new_comment)
        db.session.commit()
    return redirect(url_for('index'))
# Add this to your existing routes
@app.route('/search', methods=['GET', 'POST'])
def search():
    users = []
    if request.method == 'POST':
        query = request.form['query']
        users = User.query.filter(User.username.contains(query)).all()
    return render_template('search.html', users=users)  # Always return a response

@app.route('/follow/<int:user_id>')
def follow(user_id):
    if 'user_id' in session:
        new_follow = Follow(follower_id=session['user_id'], followed_id=user_id)
        db.session.add(new_follow)
        db.session.commit()
    return redirect(url_for('index'))
@app.route('/following')
def following():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        followed_users = User.query.join(Follow, Follow.followed_id == User.id).filter(Follow.follower_id == user.id).all()
        return render_template('following.html', followed_users=followed_users)
    return redirect(url_for('login'))

@app.route('/profile/<int:user_id>')
def profile(user_id):
    user = User.query.get(user_id)
    posts = Post.query.filter_by(user_id=user_id).all()
    return render_template('FF.html', user=user, posts=posts)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)