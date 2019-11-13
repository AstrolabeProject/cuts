FROM python:3.7
MAINTAINER Tom Hicks <hickst@email.arizona.edu>

ENV INSTALL_PATH /cuts
RUN mkdir -p $INSTALL_PATH /vos/images /vos/cutouts
WORKDIR $INSTALL_PATH

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# RUN pip install https://github.com/spacetelescope/astrocut/archive/e8125ede74716eefe9a26b6e9abbb2d9bde3d3b8.tar.gz

COPY . .

CMD [ "gunicorn", "-c", "/cuts/config/gunicorn.py", "cuts.app:create_app()" ]
