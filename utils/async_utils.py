import json
import uuid
import httpx
import utils.utils as u
from logger import logger
from typing import Optional
from collections import namedtuple
from config import TTC_BUS_API, BASE_TBILISI_URL, BASE_BATUMI_URL


async def get_tbilisi_schedule(stop_id: int, user_id: int) -> Optional[list[dict]]:
    """
    Returns json of bus schedules for a given stop.

    :param stop_id: bus stop number
    :param user_id: user's telegram id
    :return: list of dicts if the server successfully sent a response, otherwise None
    """

    # generating a unique (hopefully) ID to identify one transaction
    idx = uuid.uuid4().hex

    async with httpx.AsyncClient() as client:
        params = {
            "locale": "en",
            "ignoreScheduledArrivalTimes": "false"
        }
        headers = {"X-api-key": TTC_BUS_API}

        url = BASE_TBILISI_URL.format(bus_stop_number=stop_id)

        logger.info("HTTPX start",
                    extra={"user_id": user_id, "uuid": idx, "url": url}
        )

        response = await client.get(
            url=url,
            headers=headers,
            params=params,
        )
        response_code = response.status_code

        logger.info("HTTPX finish",
                    extra={"user_id": user_id, "uuid": idx, "response_code": response_code}
        )

        if response_code == 200:
            return response.json()
        else:
            return None


async def get_batumi_schedule(bus_stop_number: int, user_id: int) -> Optional[list[namedtuple]]:
    """
    Returns json of bus schedules for a given stop.

    :param bus_stop_number: bus stop number
    :param user_id: user's telegram id
    :return: list of namedtuples if the server successfully sent a response, otherwise None
    """

    # reading the main route database
    with open("batumi_data.json", encoding="utf-8") as file:
        data = json.load(file)

    # routes and their statuses
    for stop_id, stop_info in data["data"]["busStops"].items():
        if bus_stop_number == stop_info["BusStopNumber"]:
            bus_stop_id = stop_info["BusStopIdGeoGps"]

            routes = []
            for route_id, route_info in stop_info["routes"].items():
                routes.append(
                    u.Route(
                        id=route_id,
                        status=route_info["Status"],
                        number=data["data"]["routesNames"][route_id]["RouteNameEN"],
                    )
                )
            break
    else:
        return None

    result = []

    #setting a timeout for connection
    timeout = httpx.Timeout(10.0, read=10.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        for route in routes:
            # getting a response for each route
            params = {"routeId": route.id}

            logger.info("HTTPX start",
                        extra={"user_id": user_id, "url": f"{BASE_BATUMI_URL}?routeId={route.id}"}
            )

            response = await client.get(url=BASE_BATUMI_URL, params=params)
            response_code = response.status_code

            logger.info("HTTPX finish",
                        extra={"user_id": user_id, "response_code": response_code}
            )

            if response_code == 200:
                response_data = response.json()

                for el in response_data["data"]["arrivalTime"]:
                    if el["stop_id"] == bus_stop_id:
                        # time
                        will_arrive_in = el["arrival_times"]["first_bus"]["minute"]

                        if will_arrive_in:
                            # route
                            route_points = data["data"]["routeStatusInfo"][route.id][str(route.status)]
                            start_id, end_id = (
                                route_points["lowestId"],
                                route_points["highestId"],
                            )
                            start_name, end_name = (
                                data["data"]["busStops"][start_id]["BusStopNameEN"],
                                data["data"]["busStops"][end_id]["BusStopNameEN"],
                            )
                            result.append(
                                u.Bus(
                                    number=route.number,
                                    will_arrive_in=will_arrive_in,
                                    route=(start_name, end_name),
                                )
                            )
                        break
            else:
                continue
    return result


async def return_schedule(stop_id: int, city_name: str, user_id: int) -> str:
    """
    Returns a formatted schedule for a given stop and city if possible.

    :param stop_id: bus stop number
    :param city_name: name of the city selected by the user
    :param user_id: user's telegram id
    :return: formatted schedule or information message
    """
    # functions by cities
    schedule_funcs = {
        "Tbilisi": get_tbilisi_schedule,
        "Batumi": get_batumi_schedule,
    }

    # getting schedule depending on user's city
    schedule = await schedule_funcs[city_name](stop_id, user_id)

    if schedule:
        parse_funcs = {
            "Tbilisi": u.parse_tbilisi_schedule,
            "Batumi": u.parse_batumi_schedule
        }

        # schedule formatting
        schedule = parse_funcs[city_name](schedule)

        return schedule
    else:
        return "😢 Все автобусы уехали и в ближайшее время не ожидается."