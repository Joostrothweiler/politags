import logging
from textblob import TextBlob

from app import db

logger = logging.getLogger('score')

def compute_sentiment(article, document):
    english_blob = None
    MIN_BLOB_LENGTH = 30

    blob = TextBlob(document['text_description'])

    # Only process blobs that have sufficient text length to extract meaningful sentiment.
    if len(blob) > MIN_BLOB_LENGTH:
        logger.info(blob)

        # Make sure we have an english blob. Articles are either in dutch or in english.
        if blob.detect_language() == 'nl':
            english_blob = blob.translate(from_lang='nl', to='en')
        elif blob.detect_language() == 'en':
            english_blob = blob

        # If we were able to get an english blob, get the sentiment.
        if english_blob:
            sentiment = english_blob.sentiment

            # Store the data in the database.
            article.sentiment_polarity = sentiment.polarity
            article.sentiment_subjectivity = sentiment.subjectivity
            db.session.add(article)
            db.session.commit()