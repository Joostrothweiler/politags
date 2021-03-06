import datetime

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils import generic_relationship

from app import db


# This file defines all the different models we use.
# Migrations are automatically generated based on these classes.
# After changes, use python manage.py db revision --autogenerate -m 'Present tense message'
# Helper function to set updated certainty to the same value as the initial certainty
def same_as(column_name):
    def default_function(context):
        return context.current_parameters.get(column_name)

    return default_function


class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.String(200), primary_key=True)
    sentiment_polarity = db.Column(db.Float(), default=None, nullable=True)
    sentiment_subjectivity = db.Column(db.Float(), default=None, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Relationships
    entities = db.relationship('Entity')
    topics = db.relationship('ArticleTopic ', back_populates='article')

    @hybrid_property
    def sentiment(self):
        if self.sentiment_polarity == None:
            sentiment_polarity_description = 'Onbekend'
        elif self.sentiment_polarity < -0.6:
            sentiment_polarity_description = 'Erg negatief'
        elif self.sentiment_polarity < -0.2:
            sentiment_polarity_description = 'Negatief'
        elif self.sentiment_polarity < 0.2:
            sentiment_polarity_description = 'Neutraal'
        elif self.sentiment_polarity < 0.6:
            sentiment_polarity_description = 'Positief'
        elif self.sentiment_polarity >= 0.6:
            sentiment_polarity_description = 'Erg positief'

        if self.sentiment_subjectivity == None:
            sentiment_subjectivity_description = 'Onbekend'
        elif self.sentiment_subjectivity < 0.3:
            sentiment_subjectivity_description = 'Objectief'
        elif self.sentiment_subjectivity < 0.6:
            sentiment_subjectivity_description = 'Subjectief'
        elif self.sentiment_subjectivity >= 0.6:
            sentiment_subjectivity_description = 'Erg subjectief'

        return {
            'polarity': {
                'score': self.sentiment_polarity,
                'description': sentiment_polarity_description
            },
            'subjectivity': {
                'score': self.sentiment_subjectivity,
                'description': sentiment_subjectivity_description
            }
        }


class ArticleTopic(db.Model):
    __tablename__ = 'articles_topics'
    id = db.Column(db.Integer(), primary_key=True)
    article_id = db.Column(db.String(200), db.ForeignKey('articles.id'))
    topic_id = db.Column(db.Integer(), db.ForeignKey('topics.id'))
    initial_certainty = db.Column(db.Float(), default=0.0)
    updated_certainty = db.Column(db.Float(), default=same_as('initial_certainty'))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Hybrid properties
    @hybrid_property
    def possible_answers(self):
        return [
            {
                'id': self.topic_id
            },
            {
                'id': -1
            }
        ]

    # Relationships
    article = db.relationship('Article', back_populates='topics')
    topic = db.relationship('Topic', back_populates='articles')


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
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

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


class EntityLinking(db.Model):
    __tablename__ = 'entity_linkings'
    id = db.Column(db.Integer(), primary_key=True)
    entity_id = db.Column(db.Integer(), db.ForeignKey('entities.id'))
    initial_certainty = db.Column(db.Float(), default=0.0)
    updated_certainty = db.Column(db.Float(), default=same_as('initial_certainty'))
    linkable_type = db.Column(db.String(50))
    linkable_id = db.Column(db.Integer(), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Hybrid properties
    @hybrid_property
    def question_string(self):
        question_string = ""

        if self.linkable_type == "Politician":
            politician = self.linkable_object
            if politician.role and politician.municipality:
                question_string = 'Wordt <strong>{}</strong> van <strong>{}, {}</strong> in <strong>{}</strong> hier genoemd?'.format(
                    politician.full_name_long,
                    politician.party,
                    politician.role,
                    politician.municipality)
            elif politician.role:
                question_string = 'Wordt <strong>{}, ({})</strong> van <strong>{}</strong> hier genoemd?'.format(
                    politician.full_name_long,
                    politician.party,
                    politician.role)
            else:
                question_string = 'Wordt <strong>{}</strong> van <strong>{}</strong> in <strong>{}</strong> hier genoemd?'.format(
                    politician.full_name_long,
                    politician.party,
                    politician.municipality)

        elif self.linkable_type == 'Party':
            party = self.linkable_object

            question_string = 'Wordt <strong>{} ({})</strong> hier genoemd?'.format(party.abbreviation, party.name)

        return question_string

    @hybrid_property
    def possible_answers(self):
        return [
            {
                'id': self.linkable_id
            },
            {
                'id': -1
            },
            {
                'id': 0
            }
        ]

    # Relationships
    entity = db.relationship('Entity', back_populates='linkings')
    linkable_object = generic_relationship(linkable_type, linkable_id)

    def as_dict(self):
        return {
            'id': self.id,
            'entity_id': self.entity_id,
            'initial_certainty': self.initial_certainty,
            'updated_certainty': self.updated_certainty,
            'linkable_type': self.linkable_type,
            'linkable_id': self.linkable_id,
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


class Politician(db.Model):
    __tablename__ = 'politicians'
    id = db.Column(db.Integer(), primary_key=True)
    system_id = db.Column(db.Integer(), unique=True)
    title = db.Column(db.String(20), nullable=False, server_default=u'')
    initials = db.Column(db.String(20), nullable=False, server_default=u'')
    first_name = db.Column(db.String(50), nullable=False, server_default=u'')
    last_name = db.Column(db.String(100), nullable=False)
    party = db.Column(db.String(100), nullable=False, server_default=u'')
    municipality = db.Column(db.String(100), nullable=False, server_default=u'')
    role = db.Column(db.String(100), nullable=False, server_default=u'')
    gender = db.Column(db.String(20), nullable=False, server_default='unknown')
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    @hybrid_property
    def full_name(self):
        return self.initials + ' ' + self.last_name

    @hybrid_property
    def full_name_short(self):
        if self.initials:
            initials = str(self.initials)
            return initials[0] + '. ' + self.last_name
        else:
            return None

    @hybrid_property
    def full_name_long(self):
        if self.title and self.initials and self.first_name:
            return '{} {} ({}) {}'.format(self.title, self.initials, self.first_name, self.last_name)
        elif self.initials and self.first_name:
            return '{} ({}) {}'.format(self.initials, self.first_name, self.last_name)
        elif self.title and self.initials:
            return '{} {} {}'.format(self.title, self.initials, self.last_name)
        else:
            return self.full_name

    @hybrid_property
    def first_last(self):
        if self.first_name and self.last_name:
            return self.first_name + ' ' + self.last_name
        else:
            return None

    @hybrid_property
    def last_name_array(self):
        last_name = str(self.last_name)
        names = last_name.split('-')
        return [name.strip() for name in names]

    # API Representation
    def as_dict(self):
        return {
            'id': self.id,
            'system_id': self.system_id,
            'title': self.title,
            'initials': self.initials,
            'last_name': self.last_name,
            'full_name' : self.full_name,
            'full_name_long' : self.full_name_long,
            'full_name_short': self.full_name_short,
            'party': self.party,
            'municipality': self.municipality,
            'role': self.role,
        }


class Topic(db.Model):
    __tablename__ = 'topics'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100))

    # Relationships
    articles = db.relationship('ArticleTopic', back_populates='topic')

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }


class Verification(db.Model):
    __tablename__ = 'verifications'
    id = db.Column(db.Integer(), primary_key=True)
    verifiable_type = db.Column(db.String(50), nullable=True)
    verifiable_id = db.Column(db.Integer(), nullable=True)
    cookie_id = db.Column(db.String(200))
    response = db.Column(db.Integer(), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    verifiable_object = generic_relationship(verifiable_type, verifiable_id)
