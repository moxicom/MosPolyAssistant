# MOSPOLYASSISTANT - Speed up interaction with important information while you study

MOSPOLYASSISTANT is a telegram bot that allows you to:

- Create your own group
- Manage your group
- Create hierarchy of tags
- Join any group
- ✨Make  magic ✨

## TECH
##### python
- python-dotenv
- aiogram ```v2.25.1```
- sqlalchemy (async for PostgreSQL) ``` 2.0.21 ```
- alembic - migration
- psycopg2-binary - migration
- asyncpg ```v0.28.0```
- asyncio
 
##### USING Postgresql

## Available commands 
- ```/reg``` (Availability - all) - Starting user registration.
- ```/start``` (Availability - all) - beginning of interaction with the bot. Greeting the user, in case of administrator rights, launching the admin keyboard
- ```/help``` (Availability - all) - Showing all available functionality. Depends on the user's rights. (🔴Currently work only for admin)
- ```/get_tags``` (Availability - all) - Showing all existing tags.
- ```/get_message``` (Availability - all) - Search for a message by id.
- ```/admin_panel``` (Aveilability - admin) Get admin keyboard. (User role check is included)


User roles:
- ```0``` - basic member,
- ```1``` - modder,
- ```2``` - owner

## HOW TO USE
Better to use `linux` or `WSL`. Or you can install `make` to your windows machine.

1. Install postgres (docker image or any other way). 
2. Use next information OR open `makefile` and run commands manually.
#
1. Create venv !!! with NAME `env` !!!
   ```bash
   make venv
   ```
   1.1 **If you install manually** - activate venv

2. Install all deps to venv
   ```bash
   make install_dep
   ```

3. Create .env file
   ```env
   # .env vars
   TOKEN=<TELEGRAM_BOT_TOKEN>
   DB_USER=<DB_USER>
   DB_PASS=<DB_PASS>
   DB_HOST=<DB_HOST>
   DB_PORT=<DB_PORT>
   DB_NAME=<DB_NAME>
   ```

4. Make migration use next command
   ```bash
   make migration MIG_NAME=<MIG_NAME>
   ```
   P.S. If you have **error** there like: [alembic.util.messaging] Can't locate revision identified by '2281337e322' 
   
   try to drop all tables and repeat make command
   AND
   Create folder `migration/versions`

5. Run bot
   ```bash
   make run
   ```
