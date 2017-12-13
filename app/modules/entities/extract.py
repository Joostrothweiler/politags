from spacy.matcher import PhraseMatcher
import spacy

nlp = spacy.load('app/modules/entities/nlp_model/nlp_model_politags')
matcher = PhraseMatcher(nlp.vocab)


from app import db
from app.models.models import Article, Entity, Politician
from app.modules.common.utils import collection_as_dict
from app.modules.entities.disambiguation import politician_disambiguation, party_disambiguation

def extract_entities(document):
    # Check article is in db
    article = Article.query.filter(Article.id == document['id']).first()
    # If article is not in db, process and save everything we know
    if not article:
        return process_new_document(document)
    # Otherwise, return what we already know.
    else:
        return get_existing_knowledge(article)

def get_existing_knowledge(article):
    return {'ner' : collection_as_dict(article.entities)}


def named_entity_recognition(text_description):
    PER = nlp.vocab.strings['PER']
    doc = nlp(text_description)
    matches = matcher(doc)

    print(matches)

    for m in matches:
        match_id, start, end = m
        doc.ents += ((PER, start, end),)

    return doc.ents


def process_new_document(document):
    # First save the new article.
    new_article = Article(id = document['id'])
    db.session.add(new_article)

    # Then process the NER and save entities + disambiguation certainties
    entities = named_entity_recognition(str(document['text_description']))
    for ent in entities:
        if len(ent.text) > 1 and len(ent.text) < 50:
            entity = Entity(text = ent.text,
                            label = ent.label_,
                            start_pos = ent.start_char,
                            end_pos = ent.end_char)
            new_article.entities.append(entity)
            db.session.add(entity)

    # Separate loop for disambiguation as we want to use all entities extracted.
    for entity in new_article.entities:
        # Store disambiguation certainties
        named_entity_disambiguation(document, new_article.entities, entity)
    db.session.commit()
    # Commit changes to db
    # db.session.commit() FIXME: Do not commit so that we can experiment but not save in our database.
    # Return what we know.
    return get_existing_knowledge(new_article)


def named_entity_disambiguation(document, entities, entity):
    if entity.label == 'PER':
        politician_disambiguation(document, entities, entity)

    if entity.label == 'ORG':
        party_disambiguation(document, entities, entity)