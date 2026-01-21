# midas
Simple financial tracker on Telegram - add monocurrency incomes, expenses and get monthly reports on your monetary use.

### 📝 Expenses and incomes journal
Keep your expenses and incomes broken down by month in a telegram chat. The transactions are divided into separate categories, such as entertainment, groceries, bill, etc. At the end of the month get personalized report and advices, based on your monetary activity during the month. For repeatable tasks use events which can occur once a day, a week and a month.

### 🏦 Monitor your savings
Add storages to see how much you've got on your account at a given moment. Your bank interests are also considered - input the interest rate and see your savings multiply.

### 📌 Set financial goals
Got something you want to acquire? Midas got you covered with financial goal manager - see exactly how much you're left to save and when you'll end your goal, based on financial life in expense journal.

## Set up
Install dependencies via poetry:
```sh
poetry install
```

Setup the database with:
```sh
alembic upgrade head
poetry run seed
```

Start the application with docker by running:
```sh
docker compose up --build -d
```

The app is built with the following technologies:
* Python
* PostgreSQL
* Docker
