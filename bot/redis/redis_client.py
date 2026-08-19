from redis.asyncio import Redis

from bot.config import settings

redis: Redis = Redis.from_url(settings.redis_url, decode_responses=True)


def _cart_key(user_id: int) -> str:
    return f"cart:{user_id}"


async def add_to_cart(user_id: int, product_id: int, quantity: int) -> None:
    key = _cart_key(user_id)
    current = await redis.hget(key, str(product_id))
    new_qty = int(current or 0) + quantity
    await redis.hset(key, str(product_id), new_qty)
    await redis.expire(key, 60 * 60 * 24 * 3)  # 3 kun


async def set_cart_item(user_id: int, product_id: int, quantity: int) -> None:
    key = _cart_key(user_id)
    if quantity <= 0:
        await redis.hdel(key, str(product_id))
    else:
        await redis.hset(key, str(product_id), quantity)


async def remove_from_cart(user_id: int, product_id: int) -> None:
    await redis.hdel(_cart_key(user_id), str(product_id))


async def get_cart(user_id: int) -> dict[int, int]:
    data = await redis.hgetall(_cart_key(user_id))
    return {int(pid): int(qty) for pid, qty in data.items()}


async def clear_cart(user_id: int) -> None:
    await redis.delete(_cart_key(user_id))
