FROM python:3.6.3-jessie

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download nl

COPY . .

CMD ["python", "./manage.py", "runserver", "--host=0.0.0.0:5000"]
