import nl_core_news_sm

from spacy.matcher import PhraseMatcher
from app import db
from app.models.models import Article, Entity, Politician, Party, EntitiesPoliticians, EntitiesParties
from app.modules.common.utils import collection_as_dict, string_similarity

nlp = nl_core_news_sm.load()


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


def process_new_document(document):
    # First save the new article.
    new_article = Article(id = document['id'])
    db.session.add(new_article)

    # Then process the NER and save entities + disambiguation certainties
    doc = nlp(str(document['description']))
    for ent in doc.ents:
        if len(ent.text) > 1 and len(ent.text) < 50:
            entity = Entity(text = ent.text,
                            label = ent.label_,
                            start_pos = ent.start_char,
                            end_pos = ent.end_char)
            new_article.entities.append(entity)
            db.session.add(entity)
            # Store disambiguation certainties
            store_disambiguation(entity)

    # Commit to db
    db.session.commit()
    # Return what we know.
    return get_existing_knowledge(new_article)


def store_disambiguation(entity):
    if entity.label == 'PER':
        store_politician_disambiguation(entity)

    if entity.label == 'ORG':
        store_party_disambiguation(entity)


def store_politician_disambiguation(entity):
    possible_politicians = Politician.query.all()

    for politician in possible_politicians:
        sim = string_similarity(politician.full_name, entity.text)
        if sim > 0.4:
            a = EntitiesPoliticians(certainty = sim)
            a.politician = politician
            entity.politicians.append(a)
            db.session.add(entity)


def store_party_disambiguation(entity):
    possible_parties = Party.query.all()

    for party in possible_parties:
        sim = string_similarity(party.name, entity.text)
        if sim > 0.7:
            a = EntitiesParties(certainty = sim)
            a.party = party
            entity.parties.append(a)
            db.session.add(entity)
