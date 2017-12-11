from app import db
import datetime
from sqlalchemy.dialects import postgresql


# This file defines all the different models we use.
# Migrations are automatically generated based on these classes.
# After changes, use python manage.py db revision --autogenerate -m "Present tense message"

class Article(db.Model):
    __tablename__ = 'articles'
    # Attributes
    id = db.Column(db.String(200), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Relationships
    entities = db.relationship("Entity")

class Entity(db.Model):
    __tablename__ = 'entities'
    # Attributes
    id = db.Column(db.Integer(), primary_key=True)
    article_id = db.Column(db.String(200), db.ForeignKey('articles.id'))
    text = db.Column(db.String(50), nullable=False, server_default=u'')
    label = db.Column(db.String(50), server_default=u'')
    start_pos = db.Column(db.Integer())
    end_pos = db.Column(db.Integer())

    # Relationships
    parties = db.relationship("EntitiesParties", back_populates="entity")
    politicians = db.relationship("EntitiesPoliticians", back_populates="entity")
    article = db.relationship("Article", back_populates="entities")

    # API Representation
    def as_dict(self):
        return {'text' : self.text,
                'label': self.label,
                'start_pos': self.start_pos,
                'end_pos': self.end_pos
        }


class Politician(db.Model):
    __tablename__ = 'politicians'
    id = db.Column(db.Integer(), primary_key=True)
    system_id = db.Column(db.Integer(), unique=True)
    full_name = db.Column(db.String(100), nullable=False, server_default=u'')
    party = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    entities = db.relationship("EntitiesPoliticians", back_populates="politician")


class Party(db.Model):
    __tablename__ = 'parties'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), nullable=False, server_default=u'')
    abbreviation = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    entities = db.relationship("EntitiesParties", back_populates="party")



class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer(), primary_key=True)
    questionable_id = db.Column(db.Integer())
    questionable_type = db.Column(db.String(20))
    possible_answers = db.Column(postgresql.ARRAY(db.String(20), dimensions=1))

    # Relationships
    responses = db.relationship("Response")

    # API Representation
    def as_dict(self):
        return {'id' : self.id,
                'questionable_id': self.questionable_id,
                'questionable_type': self.questionable_type,
                'possible_answers': self.possible_answers
        }


class Response(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    question_id = db.Column(db.Integer(), db.ForeignKey('questions.id'))
    response = db.Column(db.String(100))

    question = db.relationship("Question", back_populates="responses")


# RELATIONS

class EntitiesParties(db.Model):
    __tablename__ = 'entities_parties'
    id = db.Column(db.Integer(), primary_key=True)
    entity_id = db.Column(db.Integer(), db.ForeignKey('entities.id'))
    party_id = db.Column(db.Integer(), db.ForeignKey('parties.id'))
    certainty = db.Column(db.Float(), default=0.0)

    party = db.relationship("Party", back_populates="entities")
    entity = db.relationship("Entity", back_populates="parties")



class EntitiesPoliticians(db.Model):
    __tablename__ = 'entities_politicians'
    id = db.Column(db.Integer(), primary_key=True)
    entity_id = db.Column(db.Integer(), db.ForeignKey('entities.id'))
    politician_id = db.Column(db.Integer(), db.ForeignKey('politicians.id'))
    certainty = db.Column(db.Float(), default=0.0)

    politician = db.relationship("Politician", back_populates="entities")
    entity = db.relationship("Entity", back_populates="politicians")
