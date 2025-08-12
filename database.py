import aiosqlite

async def init_db() -> None:
    """
    Initializes the database.

    :return: None
    """

    async with aiosqlite.connect("BusGE_bot.db") as db:
        await db.execute("PRAGMA foreign_keys = ON;")
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS cities (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        """
        )
        await db.execute(
            """
            INSERT INTO cities (name)
            VALUES ('Tbilisi'), ('Batumi')
        """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                city_id INTEGER,
                FOREIGN KEY (city_id) REFERENCES cities(id)
            )
        """
        )
        await db.commit()


async def user_exists(user_id: int) -> bool:
    """
    Checks if a user with the given user_id exists in the database.

    :param user_id: user's id to check
    :return: True if the user is found, otherwise NO
    """

    async with aiosqlite.connect("BusGE_bot.db") as db:
        async with db.execute(
            "SELECT COUNT(*) FROM users WHERE id = ?", (user_id,)
        ) as cursor:
            count = await cursor.fetchone()
            return count[0] > 0


async def city_selected(user_id: int) -> bool:
    """
    Checks if a user with the given user_id has selected a city

    :param user_id: user's id to check
    :return: True if the user has selected, otherwise NO
    """

    async with aiosqlite.connect("BusGE_bot.db") as db:
        async with db.execute(
            "SELECT city_id FROM users WHERE id = ? AND city_id IS NOT NULL", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row is not None


async def add_user(user_id: int) -> None:
    """
    Adds a new user to the database.

    :param user_id: user (by id) that needs to be added to the database
    :return: None
    """

    async with aiosqlite.connect("BusGE_bot.db") as db:
        await db.execute(
            """
            INSERT INTO users (id)
            VALUES (?)
        """, (user_id,)
        )
        await db.commit()


async def get_city_id(city_name: str) -> int:
    """
    Returns the ID of the received city.

    :param city_name: name of the city, which id need to get
    :return: id of the city
    """
    async with aiosqlite.connect("BusGE_bot.db") as db:
        async with db.execute(
            "SELECT id FROM cities WHERE name = ?", (city_name,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0]


async def set_city(user_id: int, city_name: str) -> None:
    """
    Sets the city selected by the user.

    :param user_id: user id for which need to set the city
    :param city_name: name of the city to set
    :return: None
    """

    async with aiosqlite.connect("BusGE_bot.db") as db:
        await db.execute(
            """
            UPDATE users
            SET city_id = (SELECT id FROM cities WHERE name = ?)
            WHERE id = ?
        """, (city_name, user_id)
        )
        await db.commit()


async def get_city_name(user_id: int) -> str:
    """
    Returns the name of the city selected by the user

    :param user_id: user id whose city need to get
    :return: user's name of the city
    """

    async with aiosqlite.connect("BusGE_bot.db") as db:
        async with db.execute(
            """
            SELECT cities.name
            FROM cities
            JOIN users ON users.city_id = cities.id
            WHERE users.id = ?
        """, (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0]