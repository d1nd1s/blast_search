# Introduction
There are 3 types of services:
- Controller
- Worker
- Webserver

Currently there should be one running **Controller**, at least one **Worker** and **Webserver**.
They communicate with each other by json messages.
When user performs a new search: 
1. **Webserver** sends a request to the **Controller**;
1. **Controller** creates new search in database and generates number of tasks to perform the search;
1. task manager within the **Controller** distributes tasks among **Workers**;
1. **Workers** execute tasks and send results to the **Controller**;
1. When all tasks for one search are completed, the **Controller** combines them and saves the result into search entry in database.
1. When user refreshes the page with a search result, **Webserver** sends request to the **Controller**. **Controller** responds with search entry as json data. If the search is still in progress, **Webserver** renders *pending_search* template. If the search is completed, **Webserver** renders a page with search result. Due to performance optimisations, **Webserver** may be configured to read search entry directly from a database.

# How to run

To start the search infrastructure one have to perform the following steps:
1. Start the **Controller**:
```
export FLASK_APP=blast_search.controller
export FLASK_ENV=development
flask run
```
2. Start **Workers**:
```
export FLASK_APP=blast_search.worker
export FLASK_ENV=development
export BLAST_CONTROLLER_URL=http://localhost:5000
export BLAST_WORKER_PORT=5050
flask run --port=$BLAST_WORKER_PORT
```
BLAST_CONTROLLER_URL should contain URL for controller.
BLAST_WORKER_PORT should contain the port value for this worker.
Port value will be sent to controller for reverse communication.
Worker has to be started on port equal to BLAST_WORKER_PORT value.
Due to Flask workflow, **Worker** need environment variable to determine its port at initialisation stage when he tells the **Controller** about himself.

3. Start **Webserver**
```
export FLASK_APP=blast_search.webserver
export FLASK_ENV=development
export BLAST_CONTROLLER_URL=http://localhost:5000
flask run --port=8080
```

4. Connect to http://localhost:8080

# Production
Please follow the following commands to run production servers with Gunicorn:

gunicorn "blast_search.webserver:create_app()"

1. Start the **Controller**:
```
gunicorn "blast_search.controller:create_app()" --bind 0.0.0.0:5000
```

2. Start **Workers**:
```
export BLAST_CONTROLLER_URL=http://localhost:5000
export BLAST_WORKER_PORT=5050
gunicorn "blast_search.worker:create_app()" \
--bind 0.0.0.0:$BLAST_WORKER_PORT
```

3. Start **Webserver**
```
export BLAST_CONTROLLER_URL=http://localhost:5000
gunicorn "blast_search.webserver:create_app()" \
--bind 0.0.0.0:8080
```

4. Connect to http://localhost:8080

