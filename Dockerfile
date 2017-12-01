FROM python:3.6.3-jessie
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
RUN pip install -U spacy
RUN python -m spacy download nl
CMD ["python", "app.py"]
