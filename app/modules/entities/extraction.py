from app import db
from app.models.models import Entity
from app.modules.common.utils import pure_len


def named_entity_recognition(article, nlp_doc):
    # Reset counts to 0 so that we can process the document again and dont have to delete entities.
    article_entities = Entity.query.filter(Entity.article_id == article.id).all()
    for entity in article_entities:
        entity.count = 0
        db.session.add(entity)

    # Count again.
    for doc_ent in nlp_doc.ents:
        entity = Entity.query.filter(Entity.article_id == article.id)\
            .filter(Entity.text == doc_ent.text)\
            .filter(Entity.label == doc_ent.label_).first()

        if entity:
            entity.count = entity.count + 1
            db.session.add(entity)
        elif has_valid_text_len(doc_ent):
            entity = Entity(text = doc_ent.text,
                            label = doc_ent.label_,
                            start_pos = doc_ent.start_char,
                            end_pos = doc_ent.end_char)
            article.entities.append(entity)
            db.session.add(entity)

    return article.entities


def has_valid_text_len(entity):
    if entity and entity.text:
        return pure_len(entity.text) > 1 and len(entity.text) < 50
    return False