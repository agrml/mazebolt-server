# Installation

* `pyenv install 3.10.0`
* `pip install poetry`
* `poetry update`
* place `sercrets/mbexam-2017-2.pk8.pem`
* run the server


# DB

1. For educational use only, install mysql on the same machine.
The server is configured to discover db on localhost.

2. Set up the db
```
$ mysql.server start
$ mysql -u root
    CREATE USER 'mazebolt'@'localhost' IDENTIFIED BY 'mazebolt';
    GRANT ALL PRIVILEGES ON * . * TO 'mazebolt'@'localhost';
    create database mazebolt;
```


# Known limitations

* We should setup gunicorn and set debug=false
* Django server does not update it's state with actual google cloud list of instances
* Django does not check attacker process state.  
    We would need a Celery instance, which would periodically send REST API requests
    to the instances and updated their sates in the DB.
* This api is too synchronous and too slow on higher load / high instance numbers. 
    Queues might help.
* Front-end is made in a fast way. If we code production, 
    I would give it to an actual fronted developer 
    or learned more Django Server-Side-Frontend capabilities at least
* I had no time for writing tests. 
    In production, we would take more time and write a few tests at least
* **Actually, about time...** It's not a half-day task at it is supposed to be.
    If I made it in production quality it would take at least 3 working days: 
  * more reliable architecture,
  * more error handling,
  * more state sync between Django, Google Cloud and Clients
  * more refactorings
  * adding tests,
  * etc.
