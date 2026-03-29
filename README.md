# midas
Midas is a simple financial tracker with user interface implemented via telegram bot (mostly because I'm bad at doing frontend).

### 📂 Transactions journal
The app provides a simple transactions journal which helps with keeping track of your financial history.

### 🔔 Events
For automating the transactions that occur regularly (monthly rent, internet bills, etc.) use events. The event will automatically transactions and notify you when the transaction is created.

### 📅 Monthly reports
At the end of each month get a personalized report of your income and expenses of the month.

## Development
Install dependencies via poetry:
```sh
poetry install
```

Setup the database with:
```sh
poetry run migrate
poetry run seed
```

Start the application with docker by running:
```sh
docker compose up --build -d
```

Run tests with:
```sh
poetry run python3 -m pytest -v
```

The app is built with the following technologies:
* Python 3.13.7
* PostgreSQL 17.6
* Docker

## Other information
Currently I'm not developing this application anymore, however here's a list of feature I'd like to implement when I come back to this project:
* Groups
* Attach documents to transactions