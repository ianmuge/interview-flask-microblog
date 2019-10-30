# Technical Assessment Submission
## Dependecies
The solution is built using flask on Python 3.7.3. \
The code ships with sample records stored in an SQlite database marked as ``news.db`` located in the project root. It also ships with a ``test.db`` used for running unit tests.

Other pertinent dependencies are listed in the requirements file
## Run instructions
- Go to project root
- Install dependencies. *_This can be done in a virtual environment as opposed to the global environment_
    ```
    pip install -r requirements.txt
    ```
- Set Flask run variables\
    On windows:\
    CMD:
    ```
    set FLASK_APP=app.py
    ```
    Powershell
    ```
    $env:FLASK_APP = "app.py"
    ```
    On *nix:
    ```
    export FLASK_APP=app.py
    ```
- Start the service
    ```
    python -m flask run
    ```
- The UI should be available on: http://127.0.0.1:5000
## To reinitialze the sqlite3 database
- Run the ``flask init-db`` command in the project root directory 
- This will generate 3 default users with 3 distinct roles, and 40 random posts.
### Default credentials
The default users generated are:
- user:
    ```
    email: user@example.com
    password: user@2019
    ```
- publisher:
    ```
    email: publisher@example.com
    password: publisher@2019
    ```
- admin:
    ```
    email: admin@example.com
    password: admin@2019
    ```
          