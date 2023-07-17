import hashlib
from math import ceil
import os
import bcrypt
from sqlalchemy import or_
from database import Session, Post, User, createPost, deletePost, deleteUser, findPost, findPostsByQuery, findUser, findUserByName, getAllCategories, getAllPosts, getAllPostsCategory, getUserPosts, saveUser, updatePost, updateUserAvatar, updateUserBio, updateUserEmail, updateUserFirstName, updateUserLastName, updateUserName
from string import punctuation, whitespace, digits, ascii_lowercase, ascii_uppercase, ascii_letters
from flask import Flask, render_template, request, redirect, flash, url_for, abort, jsonify
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from datetime import date, datetime


app = Flask(__name__)


SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    session = Session()
    user = findUser(id=user_id, session=session)
    session.close()
    return user


@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect("/home")
    else:
        return render_template("index.html")

@app.route("/home")
def home():
    session = Session()
    is_logged_in = False

    postsPerPage = 5
    currentPage = request.args.get("page", 1, type=int)
    totalPosts = session.query(Post).count() 
    totalPages = ceil(totalPosts / postsPerPage)
    offset = (currentPage - 1) * postsPerPage

    posts = getAllPosts(session=session, offset=offset, limit=postsPerPage)
    categories = getAllCategories(session=session)

    if current_user.is_authenticated:
        is_logged_in = True
        user = findUser(current_user.id, session=session)
        session.close()
        flash(f"Welcome {user.username}!")
    else:
        is_logged_in = False
        flash("Welcome guest.")

    return render_template("home.html", is_logged_in=is_logged_in, posts=posts, currentPage=currentPage, totalPages=totalPages, categories=categories)
    

@app.route("/search", methods=["POST"])
def searchPosts():
    query = request.form.get("searchQuery")
    if query:
        session = Session()

        postsPerPage = 5
        currentPage = request.args.get("page", 1, type=int)
        totalPosts = session.query(Post).filter(or_(Post.content.like(f'%{query}%'))).count()
        totalPages = ceil(totalPosts / postsPerPage)
        offset = (currentPage - 1) * postsPerPage

        posts = findPostsByQuery(query, offset=offset, limit=postsPerPage, session=session)
        session.close()
        if current_user.is_authenticated:
            if posts:
                return render_template("search.html", query=query, posts=posts, totalPages=totalPages, currentPage=currentPage, is_logged_in=True)
            else:
                message = "No results for this search query."
                return render_template("search.html", query=query, message=message, is_logged_in=True)
        else:
            if posts:
                return render_template("search.html", query=query, posts=posts, totalPages=totalPages, currentPage=currentPage, is_logged_in=False)
            else:
                message = "No results for this search query."
                return render_template("search.html", query=query, message=message, is_logged_in=False)
        
    else:
        abort(404)

@app.route("/post/<int:post_id>")
def readPost(post_id):
    session = Session()
    post = findPost(post_id, session=session)
    session.close()
    if post:
        if current_user.is_authenticated:
            return render_template("post.html", post=post, is_logged_in=True)
        else:
            return render_template("post.html", post=post, is_logged_in=False)
    else:
        abort(404)

@app.route("/user/<username>")
@login_required
def showUser(username):
    session = Session()
    user = findUserByName(username, session=session)
    session.close()
    if user:
        if current_user.is_authenticated:
            return render_template("user.html", user=user, is_logged_in=True)
        else:
            return render_template("user.html", user=user, is_logged_in=False)
    else:
        abort(404)

@app.route("/category/<category>")
def listCategoryPosts(category):
    is_logged_in = False
    if current_user.is_authenticated:
        is_logged_in = True

    session = Session()

    postsPerPage = 5
    currentPage = request.args.get("page", 1, type=int)
    totalPosts = session.query(Post).filter(Post.category == category).count() 
    totalPages = ceil(totalPosts / postsPerPage)
    offset = (currentPage - 1) * postsPerPage


    postList = getAllPostsCategory(category, offset=offset, limit=postsPerPage, session=session)
    categories = getAllCategories(session=session)

    session.close()
    return render_template("category.html", posts=postList, category=category, categories=categories, totalPages=totalPages, currentPage=currentPage, is_logged_in=is_logged_in)


@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        data = request.get_json()
        if data:
            title = data.get("title")
            content = data.get("content")
            category = data.get("category")

            session = Session()
            author = findUser(current_user.id, session=session)
            session.close()

            today = date.today()
            time = datetime.now()
            current_time = time.strftime("%H:%M:%S")
        
            if not title:
                return jsonify({'error': "Title required."})
            elif not content:
                return jsonify({'error': "Content required."})
            elif not category:
                return jsonify({'error': "Category required."})
            else:
                    session = Session()
                    post = Post(title=title, content=content, category=category, author_id=author.id, author=author.username, publication_date=today, publication_time=current_time)
                    result = createPost(post, session=session)
                    session.close()
                    if result != None:
                        jsonify({'success': False, 'error': result})
                        print("Exception occured: ", result)
                        raise Exception(result)
                    else:
                        return jsonify({'success': True, 'redirect_url': url_for("home")})

    else:
        return render_template("create.html")

        
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        session = Session()
        data = request.get_json()
        user = findUser(current_user.id, session=session)
        session.close()
        if data:
            username = data.get("username")
            email = data.get("email")
            firstName = data.get("firstName")
            lastName = data.get("lastName")
            bio = data.get("bio")

            email_hash = hashlib.md5(email.lower().encode('utf-8')).hexdigest()
            size = 200
            gravatar_url = f"https://www.gravatar.com/avatar/{email_hash}?s={size}"

            errorStatus = None
            
            if not username:
                return jsonify({'success': False, 'error': "Username required!"})
                                
            if not email:
                return jsonify({'success': False, 'error': "Email required!"})
            
            response = isValidUsername(username)
            if response is None:
                try:
                    session = Session()
                    if user.username != username:
                        errorStatus = updateUserName(user.id, username, session=session)
                    if user.email != email:
                        errorStatus = updateUserEmail(user.id, email, session=session)
        
                    updateUserFirstName(user.id, firstName, session=session)
                    updateUserLastName(user.id, lastName, session=session)   
                    updateUserBio(user.id, bio, session=session)
                    updateUserAvatar(user.id, gravatar_url, session=session)
                    session.close()
                except Exception as e:
                    return jsonify({'success': False, 'error': str(e)})
                
                if errorStatus is None:
                    return jsonify({'success': True, 'redirect_url': url_for("profile")})
                else:
                    return jsonify({'error': errorStatus})
            else:
                return response
        else:
            return jsonify({'success': False, 'error': 'No data retrieved from json.'})
    else:
        session = Session()
        user = findUser(current_user.id, session=session)
        posts = getUserPosts(user.id, session=session)
        session.close()
        if user:    
            return render_template("profile.html", user=user, posts=posts)
        else:
            abort(403)
        

@app.route("/profile/delete", methods=["GET", "POST"])
@login_required
def profileDelete():
    if request.method == "POST":
        data = request.get_json()
        if data:
            boolVal = data.get("booleanValue")
            if boolVal == True:
                session = Session()
                deleteUser(current_user.id, session=session)
                session.close()
                logout()
                return jsonify({'success': True, 'redirect_url': url_for("index")})
    else:
        abort(401)

@app.route("/profile/post-delete", methods=["GET", "POST"])
@login_required
def postDelete():
    if request.method == "POST":
        data = request.get_json()
        if data:
            boolVal = data.get("booleanValue")
            postId = data.get("postId")
            if boolVal == True:
                session = Session()
                deletePost(postId, session=session)
                session.close()
                return jsonify({'success': True})
    else:
        abort(401)

@app.route("/post/edit", methods=["POST"])
@login_required
def postEdit():
    data = request.get_json()
    if data:
        id = data.get("id")
        title = data.get("title")
        content = data.get("content")

        session = Session()
        editDate = date.today()
        editTime = datetime.now()
        updatePost(id, title, content, editDate, editTime, session=session)
        session.close()
        return jsonify({'success': True, 'redirect_url': '/post/' + id})
    else:
        return jsonify({'success': False, 'error': 'No data.'})


@app.route("/login", methods=["GET", "POST"])
def login():
    if not current_user.is_authenticated:
        try:
            if request.method == "POST":
                data = request.get_json()
                username = data.get("username")
                password = data.get("password")

                if not username:
                    return jsonify({'error': 'Username required!'})
                elif not password:
                    return jsonify({'error': 'Password required!'}) 
                else:
                    session = Session()
                    user = findUserByName(username, session=session)
                    session.close()
                    if user:             
                        if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                                login_user(user)
                                return jsonify({'success': True, 'redirect_url': url_for("home")})
                        else:
                            return jsonify({'success': False, 'error': 'Wrong password!'})
                    else:
                        return jsonify({'success': False, 'error': 'User does not exist!'})
            else:
                return render_template("login.html")
        except Exception as e:    
            return print(str(e))
    else:
        return abort(403)
    

    
@app.route("/register", methods=["GET", "POST"])
def register(): 
    if not current_user.is_authenticated:
        try:
            if request.method == "POST":
                session = Session()
                data = request.get_json()
                username = data.get("username")
                email = data.get("email")
                password = data.get("password")
                passwordConfirmation = data.get("passwordConfirmation")

                if not username:
                    return jsonify({'success': False, 'error': "Username required!"})
                elif not email:
                    return jsonify({'success': False, 'error': "Email required!"})
                elif not password:
                    return jsonify({'success': False, 'error': "Password required!"})
                elif not password == passwordConfirmation:
                    return jsonify({'success': False, 'error': "Password confirmation doesn't match."})
                elif findUserByName(username, session=session):
                    return jsonify({'success': False, 'error': "Username taken, choose another."})
                else:
                    response = isValidPassword(password)
                    if response == None:
                        response = isValidUsername(username)
                        if response == None:
                            
                            salt = bcrypt.gensalt()
                            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
                            registerDate = date.today()

                            email_hash = hashlib.md5(email.lower().encode('utf-8')).hexdigest()
                            gravatar_url = f"https://www.gravatar.com/avatar/{email_hash}?d=mp"

                            newUser = User(username=username, email=email, password=hashed, first_name=None, last_name=None, bio=None, avatar=gravatar_url, date_registered=registerDate)
                            saveUser(newUser, session=session)
                        
                            login_user(newUser)
                            session.close()
                            return jsonify({'success': True, 'redirect_url': url_for("home")})
                        else:
                            return response
                    else:
                        return response
            else:
                return render_template("register.html")
        except Exception as e:
            return print(str(e))
    else:
        return abort(403)
    
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

    
def isValidUsername(username):
    MAX_LEN = 36
    MIN_LEN = 3
    tmp = username.strip()
    usernameLen = len(tmp)

    if usernameLen < MIN_LEN or usernameLen > MAX_LEN:
        return jsonify({'error': "Username must be longer than 3 and shorter than 36 characters."})
    
    validChars = {'_', '-', '.'}
    invalidChars = set(punctuation + whitespace) - validChars
    for char in invalidChars:
        if char in tmp:
            return jsonify({'success': False, 'error': "Username contains invalid character. Valid characters are (A-Z, _, -, .)"})

        
    containsLetter = 0
    for char in tmp:
        if char in ascii_letters:
            containsLetter += 1
    
    if containsLetter < 3:
        return jsonify({'error': "Username must contain atleast 3 letters."})
        
        
def isValidPassword(password):
    new_password = password.strip() # To strip away any white spaces.
    pass_len = len(new_password)
    MAX_LEN = 20
    MIN_LEN = 6
    if pass_len < MIN_LEN or pass_len > MAX_LEN:
        return jsonify({'error': "Password must be longer than 6 and shorter than 20 characters."})
         
    valid_chars = {'-', '_', '.', '!', '@', '#', '$', '^', '&', '(', ')'}
    invalid_chars = set(punctuation + whitespace) - valid_chars
    for char in invalid_chars:
        if char in new_password:
            return jsonify({'success': False, 'error': "Password contains invalid characters, must contain only - _ . ! @ # $ ^ & ( )."})
        
    password_has_digit = False
    for char in password:
        if char in digits:
            password_has_digit = True
            break
    if not password_has_digit:
        return jsonify({'error': "Password needs atleast one digit."})
    
    password_has_lowercase = False
    for char in password:
        if char in ascii_lowercase:
            password_has_lowercase = True
            break
    if not password_has_lowercase:
        return jsonify({'error': "Passwords needs atleast one lowercase character."})
    
    password_has_uppercase = False
    for char in password:
        if char in ascii_uppercase:
            password_has_uppercase = True
            break
    if not password_has_uppercase:
        return jsonify({'error': "Password needs atleast one uppercase character."})
    