from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:bloggyblog@localhost:8889/blogz' #mysql+pymysql://username:password@localhost:8889/database name'
app.config['SQLALCHEMY_ECHO'] = True #echos SQL commands that are getting generated
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&_zP3B'

class Blog(db.Model): #db is the object we created above

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(21000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        owner = User.query.filter_by(username=username).first()
        # if user enters existing username (stored in the database) with the correct password --> and is redirected to the /newpost page with their username being stored in a session.
        if owner and owner.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        # if user enters a username that is stored in the database with an incorrect password --> redirected to the /login page with a message that their password is incorrect.
        elif owner and owner.password != password:
            flash('User password is incorrect.', 'error')
        # if user tries to login with a username that is not stored in the database and is redirected to the /login page with a message that this username does not exist.
        elif not owner:
            flash('User does not exist', 'error')
            return render_template('login.html')
        # if user does not have an account and clicks "Create Account" and is directed to the /signup page.
        else:
            return redirect('/signup')
    
    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        # TODO - validate user's data

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            # TODO - user better response messaging
            return "<h1>Choose a new username.</h1>"

    return render_template('signup.html', title="Signup")
    

@app.route('/blog', methods=['GET', 'POST'])
def blog():

        blogs = Blog.query.all()
        return render_template('blog.html', blogs=blogs)


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    owner = User.query.filter_by(username=session['username']).first()
    
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        
        if title == "":
            if body == "":
                flash("Please fill in the title and body.", "error")
                return render_template('newpost.html')
            else:
                flash("Please fill in the title.", "error")
                return render_template('newpost.html', title=title, body=body)
        else:    # NEED TO GET THE BODY ENTRY TO REMAIN
            if body == "":
                flash("Please fill in the body.", "error")
                return render_template('newpost.html', title=title, body=body)

        new_blog = Blog(title, body, owner)
        db.session.add(new_blog)
        db.session.commit()
        blog = new_blog.id

        return redirect('/displaypost?id={0}'.format(blog))


    return render_template('newpost.html')

@app.route('/displaypost', methods=['GET'])
def view_post():
    
    blog_id = request.args.get('id')
    blog = Blog.query.get(blog_id)

    if blog_id:

        title = blog.title
        body = blog.body

    return render_template('/displaypost.html', title=title, body=body)


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

if __name__ == '__main__':
    app.run()