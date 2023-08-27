from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
from pymongo import TEXT
from os import environ

app = Flask(__name__)

# MongoDB connection
username=environ.get('mongouser')
password=environ.get('mongopass')
conn_string='mongodb+srv://'+username+':'+password+'@cluster0.2viq6cu.mongodb.net/'
client = MongoClient(conn_string)
db = client.flask_db
posts = db.posts
posts.create_index([("title", TEXT), ("content", TEXT)], default_language='english')


@app.route('/')
def index():
    # Retrieve all blog posts from the database
    all_posts = posts.find()
    return render_template('index.html', posts=all_posts)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        # Get data from the form
        title = request.form.get('title')
        content = request.form.get('content')
        
        # Create a new blog post document
        new_post = {
            'title': title,
            'content': content,
            'timestamp': datetime.now()
        }
        
        # Insert the new post into the database
        posts.insert_one(new_post)
        
        return redirect(url_for('index'))
    
    return render_template('create.html')

@app.route('/post/<post_id>')
def show_post(post_id):
    # Retrieve a single blog post based on post_id
    post = posts.find_one({"_id": ObjectId(post_id)})
    return render_template('post.html', post=post)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        # Search for posts containing the search query
        search_results = posts.find({
            "$or": [
                {"title": {"$regex": search_query, "$options": "i"}},
                {"content": {"$regex": search_query, "$options": "i"}}
            ]
        })
        return render_template('search_results.html', results=search_results, query=search_query)

if __name__ == '__main__':
    app.run(debug=True)
