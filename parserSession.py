import re
from datetime import date, timedelta

import requests
from bs4 import BeautifulSoup

from logs.set_logger import logger
from parser_config import (
    ENTRYPOINT_URL,
    HOST_URL,
    MONTHS_TRANSLATE,
    RUSSIAN_MONTHS,
    RUSSIAN_WEEKDAYS,
)


class ParserSession:
    def __init__(self) -> None:
        self._session = requests.Session()
        self._cookies = ""

    @property
    def session(self) -> requests.Session:
        return self._session

    @property
    def cookies(self) -> str:
        return self._cookies

    @cookies.setter
    def cookies(self, value) -> str:
        """
        Sets the cookies value.

        Args:
            cookiesJar (RequestsCookieJar): The cookies object to set.
        """
        cookies_dict = requests.utils.dict_from_cookiejar(value)
        self._cookies = f'ORA_WWV_APP_10901={cookies_dict["ORA_WWV_APP_10901"]}; ORA_WWV_RAC_INSTANCE=2'  # noqa: E501

    def get_payload(self) -> dict:
        """
        Gets the payload parameters.

        Returns:
            dict: A dictionary that contains the payload parameters.
        """
        r = self.session.get(url=ENTRYPOINT_URL)
        # TODO: Separate the logic of initializing the cookies and
        # retrieving the payload into separate methods.
        self.cookies = r.cookies
        logger.debug("Cookies were initialized")
        url_map = self.extract_url_map(r.text)
        payload_params = self.fetch_payload_params(url_map)
        logger.debug("ParserSesssion payload params were received")
        return payload_params

    def fetch_payload_params(self, url_map: str) -> dict:
        """
        Fetches the payload parameters.

        Args:
            url_map (str): The URL map.

        Returns:
            dict: A dictionary that contains the payload parameters.
        """
        r = self.session.get(url=url_map)
        soup = BeautifulSoup(r.text, "html.parser")

        protected = soup.select_one("#pPageItemsProtected")["value"]
        p_instance = soup.select_one("#pInstance")["value"]
        salt = soup.select_one("#pSalt")["value"]
        js_obj = soup.find_all("script", type="text/javascript")[3].string
        p_request_value = re.search('\{createPluginMap\(".*?","(.*?)","', js_obj).group(
            1
        )
        p_request = "PLUGIN=" + p_request_value

        return {
            "p_instance": p_instance,
            "p_request": p_request,
            "protected": protected,
            "salt": salt,
        }

    def extract_url_map(self, response_text: str) -> str:
        """
        Extracts the URL map.

        Args:
            response_text (str): The response text.

        Returns:
            str: The URL map.
        """
        soup = BeautifulSoup(response_text, "html.parser")
        a_map_tag = soup.select_one(
            "div.t-NavigationBar-menu > ul > li:nth-child(1) > a[href]"
        )
        url_map = HOST_URL + a_map_tag.get("href", "")
        return url_map

    @staticmethod
    def generate_filename(period: str) -> str:
        """
        Generate a filename in the format "YYYY_month.json" for a given period string.

        Args:
            period (str): period in the format "Weekday, 01 Month, YYYY".

        Returns:
            str: A string representing the filename, in the format "YYYY_month.json"
        """
        match = re.search(r", 01 (\w+), (\d{4})", period)
        ru_month, year = match.groups()

        eng_month = next(
            (key for key, value in MONTHS_TRANSLATE.items() if value == ru_month), None
        )
        if not eng_month:
            raise ValueError(f"No translation found for month '{ru_month}'")

        return f"{year}_{eng_month.lower()}.json"

    @staticmethod
    def generate_template_date(input_date: date) -> str:
        """
        Generate formatted date in Russian Language.

        Args:
            input_datetime (datetime): A datetime object representing a date.

        Returns:
            str: A string representing the formatted date in Russian.
        """
        first_day_prev_month = (input_date.replace(day=1) - timedelta(days=1)).replace(
            day=1
        )
        ru_day_of_week = RUSSIAN_WEEKDAYS[first_day_prev_month.weekday()]
        ru_month = RUSSIAN_MONTHS[first_day_prev_month.month]

        formatted_date = f"{ru_day_of_week}, {first_day_prev_month:%d} {ru_month}, {first_day_prev_month:%Y}"  # noqa: E501
        return formatted_date
