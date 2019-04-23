from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:bloggyblog@localhost:8889/blogz' #mysql+pymysql://username:password@localhost:8889/database name'
app.config['SQLALCHEMY_ECHO'] = True #echos SQL commands that are getting generated
db = SQLAlchemy(app)
# drafting this for Blogz: app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model): #db is the object we created above

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(21000))

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/blog')
def blog():

    blogs = Blog.query.all()
    return render_template('blog.html', title="Build a Blog", blogs=blogs)


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
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

        new_blog = Blog(title, body)
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


if __name__ == '__main__':
    app.run()