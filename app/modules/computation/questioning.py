from app.modules.entities.extract import process_or_get_entities

def ask_first_question(article_id, data):
    entities = process_or_get_entities(article_id)

    return "Is the title '{}'?".format(data['title'])


def process_question(question_id, data):
    return response
