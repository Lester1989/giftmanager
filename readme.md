# Setup

Install poetry with `pip install poetry` if you don't have it already.

run `poetry install` to install dependencies.

have tailwind watch for changes with `tailwindcss -i input.scss -o app/static/style.css --watch` in another terminal to keep your style up to date.

# Run the app with docker

Run `docker-compose up` to start the app. The app will be available at `http://localhost:8800`.

You can have a look at the database with pgadmin at `http://localhost:8080`. The login is is specified in the `docker-compose.yml` file.

# have a look at my hosted version 

**Warning: This is a development deployment and could loose data due to updates, use the export function to store a local copy of your data!**

[https://friendshipmanager.lesterserver.de/register](https://friendshipmanager.lesterserver.de/register)



# Changes to the database

If you make changes to the database, you need to run `alembic revision --autogenerate -m "message"` to generate a migration script. Then run `alembic upgrade head` to apply the changes to the database.

# Open TODOs

- [X] dockerize
- [X] Authentication
- [X] change navigation when not logged in
- [X] create friend detail views
- [X] create friend edit views
- [X] create delete routes
- [X] use create form
- [X] REJECTED FOR NOTES add contact (whatsapp, facebook, call, mailto) links for friends
- [X] add talkingpoints to friends
- [X] create calendar view
- [X] use calendar icons for events REJECTED
- [X] add event creation
- [X] add gift creation
- [X] hide/show chips
- [X] filter events by time
- [X] add login to DB
- [X] connect login to system
- [X] add settings page
- [X] add settings for time thresolds
- [X] add registration and add registration emails
- [X] add DEMO Data for each new account
- [X] add Onboarding
- [X] add Localization
- [X] redirect to login on unauthorized error
- [X] add error handling
- [X] json import and export
- [X] add Version Tag to the footer
- [X] better sorting for friends, dates, gift ideas etc.
- [X] link to github and dockerhub in about page
- [X] add gift for event
- [X] link to be me a coffee or something similar
- [X] admin view to see users and a count of their data
- [ ] add tests
- [ ] add pydantic forms violations errorhandling
- [ ] automatic backups
- [ ] make landing page suggest to contact friend about a topic

# Pending Refactorings and Maintenance

- [X] apply SRP and create routers for each view
- [ ] create a service layer for the database
- [ ] create more tests
- [ ] add logging
- [ ] add error handling