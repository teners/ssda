##SSDA
Homework assignments implementation for software systems design and architecture class at my university.

##Task
1. Learn about data caching tools and their features to build highload applications.
2. Learn about search server options and it's configuration.

##Implemented
Database sharding, caching data in NoSQL storage, frontend and backend, searching server.

##Tools
Python, Redis, Tornado, Bootstrap, Sphinx.

##Structure
__scripts__ directory contains supplement scripts to generate MySQL database and to shard it.
__server__ contains Tornado server settings and backend stuff, HTML Tornado-style templates and static content like scripts and CSS.
__sphinx__ just contains Sphinx config file, but it apparently has to be somewhere :D

##Screenshots
Main page, here you can open user's page by it's ID
![Main page](http://i.imgur.com/JxQLZyC.png?1)
User profile (before Redis)
![Profile](http://i.imgur.com/b6SZLUQ.png?1)
User profile (after Redis)
![Profile Redis](http://i.imgur.com/Q9SU7N6.png?1)
Search fields
![Search](http://i.imgur.com/hDsCQCL.png?1)
Search results
![Search result](http://i.imgur.com/YMGo44Y.png?1)
