from app import db
import datetime
from sqlalchemy.dialects import postgresql

# This file defines all the different models we use.
# Migrations are automatically generated based on these classes.
# After changes, use python manage.py db revision --autogenerate -m "Present tense message"

class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.String(200), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Relationships
    entities = db.relationship('Entity', secondary='articles_entities',
                        backref=db.backref('articles', lazy='dynamic'))


class Entity(db.Model):
    __tablename__ = 'entities'
    id = db.Column(db.Integer(), primary_key=True)
    text = db.Column(db.String(50), nullable=False, server_default=u'', unique=True)
    label = db.Column(db.String(50), server_default=u'')


class Politician(db.Model):
    __tablename__ = 'politicians'
    id = db.Column(db.Integer(), primary_key=True)
    full_name = db.Column(db.String(100), nullable=False, server_default=u'')
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class Party(db.Model):
    __tablename__ = 'parties'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), nullable=False, server_default=u'')
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)


# Define the ArticleEntities association model
class ArticlesEntities(db.Model):
    __tablename__ = 'articles_entities'
    id = db.Column(db.Integer(), primary_key=True)
    article_id = db.Column(db.String(200), db.ForeignKey('articles.id', ondelete='CASCADE'))
    entity_id = db.Column(db.Integer(), db.ForeignKey('entities.id', ondelete='CASCADE'))


class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer(), primary_key=True)
    possible_answers = db.Column(postgresql.ARRAY(db.String(20), dimensions=1))
    responses = db.relationship("Response")


class Response(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    response = db.Column(db.String(100))
    question = db.relationship("Question", back_populates="responses")
