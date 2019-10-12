FROM python:3.7-slim
MAINTAINER Tom Hicks <hickst@email.arizona.edu>

ENV INSTALL_PATH /cuts
RUN mkdir -p $INSTALL_PATH

WORKDIR $INSTALL_PATH

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD gunicorn -b 0.0.0.0:8000 --access-logfile - "cuts.app:create_app()"
