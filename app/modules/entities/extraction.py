from app import db
from app.models.models import Entity
from app.modules.common.utils import pure_len


def named_entity_recognition(article, nlp_doc):

    for ent in nlp_doc.ents:
        entity = Entity.query.filter(Entity.article_id == article.id)\
            .filter(Entity.text == ent.text)\
            .filter(Entity.label == ent.label_).first()

        if entity:
            entity.count = entity.count + 1
        else:
            entity = Entity(text = ent.text,
                            label = ent.label_,
                            start_pos = ent.start_char,
                            end_pos = ent.end_char)
            article.entities.append(entity)

        db.session.add(entity)
        db.session.commit()

    return article.entities