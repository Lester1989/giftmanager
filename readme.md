# Setup

Install poetry with `pip install poetry` if you don't have it already.

run `poetry install` to install dependencies.

start the environment shell with `poetry shell`.

start the server with `uvicorn app.main:app --reload`.

have tailwind watch for changes with `tailwindcss -i input.scss -o app/static/style.css --watch` in another terminal to keep your style up to date.

# Changes to the database

If you make changes to the database, you need to run `alembic revision --autogenerate -m "message"` to generate a migration script. Then run `alembic upgrade head` to apply the changes to the database.

# Open TODOs

- [ ] add tests
- [ ] dockerize
- [ ] Authentication
- [ ] create detail views
- [ ] create edit views
- [X] create delete routes
- [X] use create form
- [ ] add contact (whatsapp, facebook, call, mailto) links for friends
- [ ] add social media links for friends
- [ ] add talkingpoints to friends
- [ ] create calendar view
- [ ] hide/show chips
- [ ] make landing page suggest to contact friend about a topic
