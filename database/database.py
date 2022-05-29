import logging

import asyncio
import aiomysql
import config
from entity.entity import Metric


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
    print("Got DB response: " + str(result))
    metrics_res = []
    for metric in result:
        will_be_added = Metric()
        will_be_added.id = metric[0]
        will_be_added.user_id = metric[1]
        will_be_added.name = metric[2]
        metrics_res.append(will_be_added)
    conn.close()
    return metrics_res


async def delete_metric(metric_id, loop):
    conn = await get_connection(loop)
    cur = await conn.cursor()
    await cur.execute("delete from metric where id = %s", (int(metric_id)))
    await conn.commit()
    conn.close()

async def get_users(loop) -> dict:
    conn = await get_connection(loop)
    cur = await conn.cursor()
    await cur.execute("select user.id, metric.id as metric_id, metric.name as metric_name from user right join metric on metric.user_id = user.id")
    result = await cur.fetchall()
    user_metrics: dict
    user_metrics = {}
    for user in result:
        user_stats = user_metrics.get(str(user[0]))
        if user_stats == None:
            user_stats = []
        metric = Metric()
        metric.id = user[1]
        metric.name = user[2]
        user_stats.append(metric)
        user_metrics[str(user[0])] = user_stats

    print(user_metrics)
    conn.close()
    return user_metrics

async def rate_metric(metric_id, rating, loop):
    conn = await get_connection(loop)
    cur = await conn.cursor()
    await cur.execute(
        "insert into grade (metric_id, rate) values (%s, %s) ON DUPLICATE KEY UPDATE rate = values(rate);",
        (int(metric_id), int(rating)))
    await conn.commit()
    conn.close()

async def get_contributions(user_id, loop):
    conn = await get_connection(loop)
    cur = await conn.cursor()
    await cur.execute(
        "select count(*) as cnt from `user` "
        "right join metric on `user`.id = metric.user_id "
        "right join grade on grade.metric_id = metric.id "
        "where user.id = %s;",
        (int(user_id)))
    result = await cur.fetchall()
    print(result)
    cnt = result[0][0]
    print("Total: " + str(cnt))
    return cnt
