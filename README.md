# bungie-api-java

This project will generate a Java library for the Bungie API.

Intended to allow a user easily call bungie-api endpoints. Endpoint responses returned as an Object rather than raw Json for easier implementation.

* Run "generator.py" to create "generated-src" folder.  This folder will include api (endpoints), enums, and models subfolders.

* End User can call endpoint methods and then use getters to navigate responses

*Helper folder for HttpUtils, OAuth, and ResponseObject will be added when ready*

*NOTE: Generated-src uses com.google.gson*
