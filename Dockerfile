FROM python:3.7.5

MAINTAINER Tom Hicks <hickst@email.arizona.edu>

ENV INSTALL_PATH /cuts
RUN mkdir -p $INSTALL_PATH /vos/images /vos/cutouts
WORKDIR $INSTALL_PATH

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD [ "gunicorn", "-c", "/cuts/config/gunicorn.py", "cuts.app:create_app()" ]
