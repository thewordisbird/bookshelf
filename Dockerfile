FROM python:3.7

# Set directory for app:
WORKDIR /usr/src/app

# Install and update system dependencies:
RUN apt-get -yqq update

# Copy all files to container:
COPY . .

# Install app requirements and app as editable package (for testing only)
RUN pip install -r requirements.txt

ENV PORT 8080
CMD exec gunicorn --bind :$PORT --workers 4 --threads 8 "bookshelf:create_app()"
