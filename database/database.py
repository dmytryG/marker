import logging

import asyncio
import aiomysql
import config

async def get_connection(loop):
    return await aiomysql.connect(host=config.DB_HOST, port=3306,
                                  user=config.DB_USER, password=config.DB_PASS, db=config.DB_NAME,
                                  loop=loop)

async def test_example(loop):
    conn = await get_connection(loop)
    cur = await conn.cursor()
    tables = open("res/tables.sql").read()
    await cur.execute(tables)
    print("Tablse crated")
    await conn.commit()
    conn.close()


async def add_user(id, username, loop):
    conn = await get_connection(loop)
    cur = await conn.cursor()
    await cur.execute("insert into user (id, username) values (%s,%s)", (int(id), username))
    logging.info("inserting user:" + str(id) + ", " + username)
    await conn.commit()
    conn.close()
    #print("inserting user:" + id + ", " + username)
    #connection.execute("insert into user (id, username) values (%s,%s)", (int(id), str(username)))

async def add_metric(user_id, name, loop):
    conn = await get_connection(loop)
    cur = await conn.cursor()
    await cur.execute("insert into metric (user_id, name) values (%s,%s)", (int(user_id), name))
    logging.info("Creating new metric for: " + str(user_id) + ", with name: " + name)
    await conn.commit()
    conn.close()

async def get_metrics(user_id, loop):
    conn = await get_connection(loop)
    cur = await conn.cursor()
    await cur.execute("select * from metric where user_id = %s", (int(user_id)))
    logging.info("Getting metrics for: " + str(user_id))
    result = await cur.fetchall()
    #print(result)
    conn.close()
    return result

