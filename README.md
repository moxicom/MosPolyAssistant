# MOSPOLYASSISTANT
## _Speed up interaction with important information while you study_

MOSPOLYASSISTANT is a telegram bot that allows you to:

- Create your own group
- Manage your group
- Create hierarchy of tags
- Join any group
- ✨Make  magic ✨

> We hope that this bot
> will help you

## TECH
##### python
- python-dotenv
- aiogram ```v2.25.1```
- sqlalchemy (async for PostgreSQL) ``` 2.0.21 ```
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
