import json


def write_classifier_training_file(document, feature_vector, candidate):
    # check if candidate is actually in document evaluation file and assign label based on this.
    candidate_in_document = candidate_present_in_document(document, candidate)

    line = ''
    for f in feature_vector:
        line += '{},'.format(f)
    line += (str(candidate_in_document) + '\n')

    if candidate_in_document:
        print('This is the actual candidate!: [{}] / {} ({})'.format(feature_vector, candidate.full_name, candidate.party))


    with open('app/modules/entities/nlp_model/tooling/training/features_test.txt', 'a') as my_file:
        my_file.write(line)


def candidate_present_in_document(document, candidate):
    eval_data_dijk = json.load(open('data_resources/evaluation/van_dijk_eval.json'))
    eval_data_new = json.load(open('data_resources/evaluation/new_test_eval.json'))
    eval_doc = None
    candidate_in_document = False

    for doc in eval_data_dijk['items']:
        if doc['article_id'] == document['id']:
            eval_doc = doc

    for doc in eval_data_new['items']:
        if doc['article_id'] == document['id']:
            eval_doc = doc

    for politician in eval_doc['politicians']:
        if politician['system_id'] == candidate.system_id:
            candidate_in_document = True

    return candidate_in_document