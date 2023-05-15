Flask/MongoDB/Docker
===============
Refer to API-info.txt in each app.In addition to app.py you will find a

messages.py :

-   responses for the requests

Installation
--------------
-   Install docker 
-   docker-compose build
-   docker-compose up

store_retrieve
--------------

A simple user registration with additional two resources
['/store','/get'] to store and retrieve a sentence from
database.

text-compare
--------------

Make use of spacy to check for similiraties in two sentences
if the user has enough tokens.

classify
--------------
Make use of keras inceptionV3. The app takes an image url and gives
the top 5 predictions.


bankapi
--------------

A simple bank API to take loan and pay debts
