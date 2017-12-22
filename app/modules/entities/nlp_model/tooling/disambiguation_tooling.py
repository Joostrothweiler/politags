import json


def write_classifier_training_file(document, feature_vector, candidate):
    # check if candidate is actually in document evaluation file and assign label based on this.
    candidate_in_document = candidate_present_in_document(document, candidate)

    with open('app/modules/entities/nlp_model/tooling/features.txt', 'a') as my_file:
        my_file.write(
            '{},{},{},{},{}\n'.format(feature_vector[0], feature_vector[1], feature_vector[2], feature_vector[3],
                                      candidate_in_document))


def candidate_present_in_document(document, candidate):
    eval = 'data_resources/evaluation/van_dijk_eval.json'
    eval_data = json.load(open(eval))
    eval_doc = None
    candidate_in_document = False

    for doc in eval_data['items']:
        if doc['article_id'] == document['id']:
            eval_doc = doc

    print(document['id'])
    print(eval_doc['article_id'])

    for politician in eval_doc['politicians']:
        if politician['system_id'] == candidate.system_id:
            candidate_in_document = True

    return candidate_in_document