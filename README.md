# Friendsletter

## Overview

This is a small app that uses a Gmail account to collect emails from a predefined list of friends over some period (the default is 14 days). Then, at the end of that period, it sends a newsletter to everyone on the list with everyone's contributions over the period, including the received emails, image attachments, and a visual calendar display (using a shared Google calendar) showing the upcoming events over the next period.

The setup is fairly manual at the moment, so programming experience is somewhat required.

## Setup

### Requirements

- A list of all your friends' email addresses
- A Google Cloud project (under your personal Google account)
- A new Gmail account, to be your newsletter user
- A Google Calendar created by the newsletter user, and shared with your list of friends
- `uv` Python package manager installed
- `sqlite3` installed

### Steps

1. Clone the repo and install it with `uv sync`
2. Create a config file `config.toml` and use the example config file included to fill out the needed values. Everything can stay the same except for the email address and calendar URL.
3. In your Google Cloud project, enable the Gmail API and Google Calendar API.
4. In Google Cloud, Go to Google Auth Platform, then the Audience tab on the left. Here, add your newsletter user as a test user.
5. On the same page, go to the Clients tab. Create an OAuth 2 client of type "Desktop app" and give it a name. You will then be able to download the credentials as a JSON file. Put this file in this repo's root and rename it `client_secrets.json`.
6. On the same page, go to the Data Access tab. Add two scopes: `auth/gmail.readonly` and `auth/calendar`. You're finished with the Google Cloud steps!
7. Back in the repo root, create a sqlite3 database by running `sqlite3 friendsletter.db`.
8. Choose what day you want to start collecting emails in YYYY-MM-DD format. **This must be a Sunday, to make the calendar format nicely.** Seed the database with the start date by running
```sql
CREATE TABLE start_date (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL
);
INSERT INTO start_date (date) VALUES ("YYYY-MM-DD");
```
9. Create a CSV file `friends.csv` of the form `name,email` of all your friends. Only emails from people on this list will be stored. Example:
```csv
name,email
Bob,bob@email.com
Alice,alice@email.com
```
10. You're ready to start listening for emails. Run `uv run start`. Your browser should open, requesting access to your Google account. Make sure to use your newsletter user to accept this request.
11. Now, over the defined period of time (the default is 14 days), the app will collect emails from your friends. Once the period has elapsed, it will send an email to all your friends, and then update the start date to today.

## Tests

Run `APP_ENV=test uv run pytest` to run the tests.

