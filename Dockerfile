FROM python:3.10-alpine

ARG git_hash
ARG build_date

RUN mkdir /app
COPY . /app
WORKDIR /app

RUN cat version_info.py | sed s/%GIT_HASH%/$git_hash/ | sed s/%BUILD_DATE%/$build_date/ > version_info_updated.py
RUN mv version_info_updated.py version_info.py

RUN pip install --upgrade pip
RUN pip install pipenv
RUN pipenv install --system --deploy

CMD ["python", "fff.py"]
