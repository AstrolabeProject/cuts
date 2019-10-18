FROM python:3.7-slim
MAINTAINER Tom Hicks <hickst@email.arizona.edu>

ENV INSTALL_PATH /cuts
RUN mkdir -p $INSTALL_PATH
WORKDIR $INSTALL_PATH

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD gunicorn -c "python:config.gunicorn" "cuts.app:create_app()"
