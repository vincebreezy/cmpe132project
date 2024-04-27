CMPE132 SJSU Library Project

Role based access control project to simulate the SJSU Library website using Flask. 

## In Visual Studio Code WSL terminal
1. `git clone https://github.com/vincebreezy/cmpe132project`
2. `pip install -e .`
3. `flask --app website init-db`
4. `sqlite3 < ./tests/prefill-db.sql`
5. Start website: `flask --app website run`
6. Website can be found on http://127.0.0.1:5000

