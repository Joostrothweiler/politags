from app import db
from app.models.models import Entity, Article
from app.modules.common.utils import pure_len


def named_entity_recognition(article: Article, nlp_doc) -> list:
    """
    Perform Named Entity Recognition on the article in the database, including all types such as LOC, MISC
    :param article: article in the database
    :param nlp_doc: NLP processed document
    :return: database entities for this article.
    """
    # Reset counts to 0 so that we can process the document again and dont have to delete entities.
    article_entities = Entity.query.filter(Entity.article_id == article.id).all()
    for entity in article_entities:
        entity.count = 0
        db.session.add(entity)

    # Count again.
    for doc_ent in nlp_doc.ents:
        entity = Entity.query.filter(Entity.article_id == article.id) \
            .filter(Entity.text == doc_ent.text) \
            .filter(Entity.label == doc_ent.label_).first()

        if entity:
            db.session.add(entity)
            entity.count += 1
        elif entity_text_has_valid_length(doc_ent):
            # Strip the entity text so that we have no empty space at the ends.
            doc_ent_text = doc_ent.text.strip()
            # Create the entity in the database.
            entity = Entity(text=doc_ent_text,
                            label=doc_ent.label_,
                            start_pos=doc_ent.start_char,
                            end_pos=doc_ent.end_char)
            article.entities.append(entity)
            db.session.add(entity)

    return article.entities


def entity_text_has_valid_length(entity) -> bool:
    """
    Check whether the entity has a valid entity.text length such that we can insert it in the database.
    :param entity: NLP entity processed by Spacy.
    :return: Boolean whether entity has valid text length.
    """
    if entity and entity.text:
        return pure_len(entity.text) > 1 and len(entity.text) < 50
    return False
