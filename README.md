CMPE132 SJSU Library Project

Role based access control project to simulate the SJSU Library website using Flask. 

## In Visual Studio Code WSL terminal
1. `pip install -e .`
2. `flask --app website init-db`
3. `sqlite3 < ./tests/prefill-db.sql`
4. Start website: `flask --app website run`
5. Website can be found on http://127.0.0.1:5000
