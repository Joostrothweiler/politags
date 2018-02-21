from app.modules.human_computation.questioning import generate_questions, process_entity_verification, \
    process_topic_verification


def fetch_article_question(document, cookie_id):
    response = generate_questions(document, cookie_id)
    return response


def post_entity_linking_verification(document, param_entity_linking_id, cookie_id, response_id):
    response = process_entity_verification(document, param_entity_linking_id)
    return response

# FIXME: Either pass article to all verification api calls or to none.
def post_topic_verifications(document, article_id, cookie_id, topic_response):
    response = process_topic_verification(article_id, cookie_id, topic_response)
    return response
