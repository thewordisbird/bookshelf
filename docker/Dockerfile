FROM python:3.7

RUN mkdir /usr/src/requirements
RUN mkdir /usr/src/app

# Set directory for app:
WORKDIR /usr/src/app

# Make directories for requirements and code
COPY requirements /usr/src/requirements
RUN pip install -r /usr/src/requirements/development.txt

