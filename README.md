# bookshelf
A web application to rate and review books.

[bookshelf.thewordisbird.dev](https://bookshelf.thewordisbird.dev)

## Motivation
A project to learn and implement a python flask application using Google's Firebase cloud services. At this point this includes Firebase Auth and Firestore. Updates will include Firebase Storage to store user profile images, Firebase Hosting to take advantage of serving staic files over a CDN, and Firebase Cloud Functions to manage firestore maintnance.

## Technologies
* Backend
    * Python 3.7
    * Flask
    * Firebase Authentication
    * Firebase Firestore
* Frontend
    * html/CSS
    * Materialize CSS
    * JavaScript 
* Hosting
    * Google Cloud Run
    * Docker
* External Data
    * Google Books REST API

## Setup/Installation
Before installation the following external services are required: 
* A [Firebase](https://firebase.google.com) account is required along with a seperate project for development and testing.
* A [Google Cloud] (https://cloud.google.com) account with the secrets manager api enabled with the following secrets:
    * SECRET_KEY - used by flask for CSRF protection
    * WEB_API_KEY - used by Firebase for REST api requests.
* Install [Docker](https://docker.com).

Clone repository:
    git clone https://github.com/thewordisbird/bookshelf.git

Setup secrets, local keys, and config files:
* This app uses the google secrets manager api. The following secrets are required for every connected project (production, development, testing, etc.):
    * SECRET_KEY 
    * WEB_API_KEY
* Download and save Firebase Service Account Key for each project (production, development, testing, etc.).
* Update the following fields for all files in /config:
    * PROJECT_ID
    * GOOGLE_APPLICATION_CREDENTIALS
* Add Firebase SDK snippet to /bookshelf/scripts/init.js

## Usage
The application is controlled in the manage.py file. This file will set all the relevant config values for the desired run enviornment and build the docker file based off the appropriate .yml docker-compose file.
* Run locally in development mode. Runs on localhost:5000.  
    $ ./manage.py compose up
* Stop locally run instance:  
    $ ./manage.py compose down
* Run tests.  
    $ ./manage.py test

## License
MIT License


