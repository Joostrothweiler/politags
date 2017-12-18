from sqlalchemy.ext.hybrid import hybrid_property

from app import db
import datetime
from sqlalchemy.dialects import postgresql
from sqlalchemy_utils import generic_relationship


# This file defines all the different models we use.
# Migrations are automatically generated based on these classes.
# After changes, use python manage.py db revision --autogenerate -m 'Present tense message'
class Article(db.Model):
    __tablename__ = 'articles'
    # Attributes
    id = db.Column(db.String(200), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Relationships
    entities = db.relationship('Entity')

class Entity(db.Model):
    __tablename__ = 'entities'
    # Attributes
    id = db.Column(db.Integer(), primary_key=True)
    article_id = db.Column(db.String(200), db.ForeignKey('articles.id'))
    text = db.Column(db.String(50), nullable=False, server_default=u'')
    label = db.Column(db.String(50), server_default=u'')
    start_pos = db.Column(db.Integer())
    end_pos = db.Column(db.Integer())
    count = db.Column(db.Integer(), default=1)

    # Relationships
    article = db.relationship('Article', back_populates='entities')
    linkings = db.relationship('EntityLinking', back_populates='entity')

    # API Representation
    def as_dict(self):
        return {
            'id': self.id,
            'article_id': self.article_id,
            'text': self.text,
            'label': self.label,
            'start_pos': self.start_pos,
            'end_pos': self.end_pos,
            'count': self.count
        }


class Politician(db.Model):
    __tablename__ = 'politicians'
    id = db.Column(db.Integer(), primary_key=True)
    system_id = db.Column(db.Integer(), unique=True)
    first_name = db.Column(db.String(50), nullable=False, server_default=u'')
    last_name = db.Column(db.String(100), nullable=False, server_default=u'')
    party = db.Column(db.String(100), nullable=False, server_default=u'')
    municipality = db.Column(db.String(100), nullable=False, server_default=u'')
    role = db.Column(db.String(100), nullable=False, server_default=u'')
    level_of_ambiguity = db.Column(db.Float(), default=0.0)  # TODO: We should probably remove this attribute.
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    @hybrid_property
    def full_name(self):
        return self.first_name + ' ' + self.last_name

    # API Representation
    def as_dict(self):
        return {
            'id': self.id,
            'system_id': self.system_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'party': self.party,
            'municipality': self.municipality,
            'role': self.role,
        }


class Party(db.Model):
    __tablename__ = 'parties'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), nullable=False, server_default=u'')
    abbreviation = db.Column(db.String(20), nullable=False, server_default=u'')
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # API Representation
    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'abbreviation': self.abbreviation
        }


class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer(), primary_key=True)
    question_string = db.Column(db.String(200))
    possible_answers = db.Column(postgresql.ARRAY(db.String(20), dimensions=1))
    questionable_type = db.Column(db.String(50))
    questionable_id = db.Column(db.Integer(), nullable=False)

    # Relationships

    responses = db.relationship('Response', back_populates='question')
    questionable_object = generic_relationship(questionable_type, questionable_id)

    # API Representation
    def as_dict(self):
        return {
            'id': self.id,
            'questionable_id': self.questionable_id,
            'questionable_type': self.questionable_type,
            'possible_answers': self.possible_answers
        }


class Response(db.Model):
    __tablename__ = 'responses'
    id = db.Column(db.Integer(), primary_key=True)
    question_id = db.Column(db.Integer(), db.ForeignKey('questions.id'))
    response = db.Column(db.String(100))

    question = db.relationship('Question', back_populates='responses')


# RELATIONS
class EntityLinking(db.Model):
    __tablename__ = 'entity_linkings'
    id = db.Column(db.Integer(), primary_key=True)
    entity_id = db.Column(db.Integer(), db.ForeignKey('entities.id'))
    certainty = db.Column(db.Float(), default=0.0)
    linkable_type = db.Column(db.String(50))
    linkable_id = db.Column(db.Integer(), nullable=False)

    entity = db.relationship('Entity', back_populates='linkings')
    linkable_object = generic_relationship(linkable_type, linkable_id)
