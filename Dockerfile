FROM python:3.7.9

MAINTAINER Tom Hicks <hickst@email.arizona.edu>

ARG TESTS=notests

ENV RUNNING_IN_CONTAINER True
ENV INSTALL_PATH /cuts

RUN mkdir -p $INSTALL_PATH /vos/images /vos/cutouts

WORKDIR $INSTALL_PATH

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY config config
COPY instance instance
COPY .bash_env /etc/trhenv
COPY cuts cuts
COPY $TESTS $TESTS

CMD [ "gunicorn", "-c", "/cuts/config/gunicorn.py", "-e", "SCRIPT_NAME=/cuts", "cuts.app:create_app()" ]
