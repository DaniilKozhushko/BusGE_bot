import json
import httpx
import utils.utils as u
from collections import namedtuple
from typing import Optional
from config import TTC_BUS_API, BASE_TBILISI_URL, BASE_BATUMI_URL


async def get_tbilisi_schedule(stop_id: int) -> Optional[list[dict]]:
    """
    Returns json of bus schedules for a given stop.

    :param stop_id: bus stop number
    :return: list of dicts if the server successfully sent a response, otherwise None
    """

    async with httpx.AsyncClient() as client:
        params = {
            "locale": "en",
            "ignoreScheduledArrivalTimes": "false"
        }
        headers = {"X-api-key": TTC_BUS_API}
        response = await client.get(
            url=BASE_TBILISI_URL.format(bus_stop_number=stop_id),
            headers=headers,
            params=params,
        )
        if response.status_code == 200:
            return response.json()
        else:
            return None


async def get_batumi_schedule(bus_stop_number: int) -> Optional[list[namedtuple]]:
    """
    Returns json of bus schedules for a given stop.

    :param bus_stop_number: bus stop number
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
            response = await client.get(url=BASE_BATUMI_URL, params=params)
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
    return result


async def return_schedule(stop_id: int, city_name: str) -> str:
    """
    Returns a formatted schedule for a given stop and city if possible.

    :param stop_id: bus stop number
    :param city_name: name of the city selected by the user
    :return: formatted schedule or information message
    """
    # functions by cities
    schedule_funcs = {
        "Tbilisi": get_tbilisi_schedule,
        "Batumi": get_batumi_schedule,
    }

    # getting schedule depending on user's city
    schedule = await schedule_funcs[city_name](stop_id)

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