from flask_login import UserMixin
from sqlalchemy import Boolean, Date, LargeBinary, Time, ForeignKey, Text, create_engine, Column, String, Integer, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session, sessionmaker, scoped_session


db_connection_string = ("your-connection-string")

engine = create_engine(db_connection_string, future=True, pool_size=20, max_overflow=10) #SSL can be added via connect_args
Base = declarative_base()   

class User(Base, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(16), unique=True, nullable=False)
    email = Column(String(320), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    first_name = Column(String(32))
    last_name = Column(String(32))
    bio = Column(String(300))
    avatar = Column(String(512))
    date_registered = Column(Date)
    posts = relationship('Post', backref='written_by', cascade='all, delete')
    
class Post(Base):   
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    author = Column(String(16), nullable=False)
    title = Column(String(64), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(Text)
    publication_date = Column(Date, nullable=False) 
    publication_time = Column(Time, nullable=False)
    edited = Column(Boolean)
    edited_date = Column(Date)
    edited_time = Column(Time)

Base.metadata.create_all(bind=engine)
session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Session = scoped_session(session_factory)


# All the User class methods
def findUser(id, session):
    user = session.query(User).get(id)
    return user
        
def findUserByName(name, session):
    user = session.query(User).filter(User.username == name).first()
    return user
        

def saveUser(user, session):
    
    try:
        session.add(user)
    except Exception as e:
        session.rollback()
        print(str(e))
        raise
    else:
        session.commit()


def deleteUser(id, session):
    user = session.query(User).get(id)
    if user:
        try:
            session.delete(user)
        except Exception as e:
            session.rollback()
            print(str(e))
            raise
        else:
            session.commit()
    else:
        print("Error: User doesn't exist. [deleteUser method]")

def updateUserName(id, newUserName, session):
        user = session.query(User).get(id)
        if user:
            username_check = session.query(User).filter(User.username == newUserName, User.id != user.id).first()
            if username_check is not None:
                return "Username is already taken!"
            else:
                try:
                    user.username = newUserName
                except Exception as e:
                    session.rollback()
                    print(str(e))
                    raise
                else:
                    session.commit()
                    return None
        else:
            print("Error: User doesn't exist. [updateUserName method]")

def updateUserEmail(id, newEmail, session):
        user = session.query(User).get(id)
        if user:
            email_check = session.query(User).filter(User.email == newEmail, User.id != user.id).first()
            if email_check is not None:
                return "Email is already taken!"
            else:
                try:
                    user.email = newEmail
                except Exception as e:
                    session.rollback()
                    print(str(e))
                    raise
                else:
                    session.commit()
                    return None
        else:
            print("Error: User doesn't exist. [updateUserEmail method]")
        

def updateUserFirstName(id, firstName, session):
        user = session.query(User).get(id)
        if user:
            try:
                user.first_name = firstName
            except Exception as e:
                session.rollback()
                print(str(e))
                raise
            else:
                session.commit()
        else:
            print("Error: User doesn't exist. [updateUserFirstName method]")

def updateUserLastName(id, lastName, session):
        user = session.query(User).get(id)
        if user:
            try:
                user.last_name = lastName
            except Exception as e:
                session.rollback()
                print(str(e))
                raise
            else:
                session.commit()
        else:
            print("Error: User doesn't exist. [updateUserLastName method]")


def updateUserBio(id, bio, session):
        user = session.query(User).get(id)
        if user:
            try:
                user.bio = bio
            except Exception as e:
                session.rollback()
                print(str(e))
                raise
            else:
                session.commit()
        else:
            print("Error: User doesn't exist. [updateUserBio method]")
            
def updateUserAvatar(id, avatar, session):
        user = session.query(User).get(id)
        if user:
            try:
                user.avatar = avatar
            except Exception as e:
                session.rollback()
                print(str(e))
                raise
            else:
                session.commit()


# All the Post class methods
def createPost(post, session):
        try:
            session.add(post)
        except Exception as e:
            session.rollback()
            return str(e)
        else:
            session.commit()


def deletePost(id, session):
        try:
            post = session.query(Post).get(id)
            session.delete(post)
        except Exception as e:
            print("Exception occured: ", str(e))
            session.rollback()
            raise e
        else:
            session.commit()

def updatePost(id, title, content, date, time, session):
        try:
            post = session.query(Post).get(id)
            post.title = title
            post.content = content
            post.edited = True
            post.edited_date = date
            post.edited_time = time
        except Exception as e:
            session.rollback()
            print("Exception occured: ", str(e))
            raise e
        else:
            session.commit()
        

def getAllPosts(session, offset, limit):
        try:
            query = session.query(Post).order_by(Post.id.desc()).offset(offset).limit(limit)
            posts = query.all()
        except Exception as e:
            print("Exception occured: ", str(e))
            raise e
        else:
            return posts
        
def getUserPosts(id, session):
        try:
            posts = session.query(Post).filter(Post.author_id == id).all()
        except Exception as e:
            print("Exception occured: ", str(e))
            raise e
        else:
            return posts
        
def getAllPostsCategory(category, offset, limit, session):
        try:
            query = session.query(Post).order_by(Post.id.desc()).filter(Post.category == category).offset(offset).limit(limit)
            posts = query.all()
        except Exception as e:
            print("Exception occured: ", str(e))
            raise e
        else:
            return posts
        
def findPost(id, session):
        try:
            post = session.query(Post).filter(Post.id == id).first()
        except Exception as e:
            print("Exception occured: ", str(e))
            raise e
        else:
            return post
        
def findPostsByQuery(query, offset, limit, session):
        try:
            temp = session.query(Post).order_by(Post.id.desc()).filter(or_(Post.content.like(f'%{query}%'))).offset(offset).limit(limit)
            posts = temp.all()
            print(posts)
        except Exception as e:
            print("Exception occured: ", str(e))
            raise e
        else:
            return posts
        
def getAllCategories(session):
        try:
            categories = session.query(Post.category).distinct()
        except Exception as e:
            print("Exception occured: ", str(e))
            raise e
        else:
            return categories
    



        

