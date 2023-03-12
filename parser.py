import json
import re
from typing import Dict, List

from bs4 import BeautifulSoup
from tqdm import tqdm

from parser_config import (
    AJAX_URL,
    DISTRICT_PATTERN,
    HOST_URL,
    LINK_PATTERN,
    MALFUNCTION_TYPE_PATTERN,
    PERFORMER_PATTERN,
    TICKET_NUMBER_PATTERN,
)
from parser_session import ParserSession
from protocol_constants import set_apls_headers, set_ticket_headers, set_ticket_payload


class Parser:
    def __init__(
        self, session, cookies, p_instance, p_request, protected, salt
    ) -> None:
        """
        Initializes a Parser object with session parameters, cookies, and other data.

        Args:
            session (requests.sessions.Session): An instance of a Requests session.
            cookies (dict): A dictionary of cookies to use in the Requests session.
            p_instance (str): The p_instance parameter used in the POST request payload.
            p_request (str): The p_request parameter used in the POST request payload.
            protected (str): The protected parameter used in the POST request payload.
            salt (str): The salt parameter used in the POST request payload.
        """
        self.session = session
        self.cookies = cookies
        self.p_instance = p_instance
        self.p_request = p_request
        self.protected = protected
        self.salt = salt
        self.ticket_headers = {}

    def parse_ticket_html(self, html_doc: str) -> dict:
        """
        Parses the HTML of a ticket page and extracts relevant data.

        Args:
            html_doc (str): The HTML of a ticket page.

        Returns:
            dict: A dictionary containing the extracted data, including
            status, dates, comments, and ratings.
        """
        soup = BeautifulSoup(html_doc, "html.parser")

        request_status = soup.select_one("div.current_problem_status > span")
        request_status = request_status.contents[0].strip() if request_status else ""

        request_status_date = soup.select_one("div.current_problem_status_date")
        request_status_date = (
            request_status_date.contents[0].strip() if request_status_date else ""
        )

        user_comment = soup.select_one("div.t-Region-body > div:nth-child(2)")
        user_comment = (
            user_comment.contents[1].replace("\r", "").replace("\n", " ").strip()
            if user_comment
            else ""
        )

        organization_comment = soup.select_one("div.t-Region-body > div:nth-child(3)")
        organization_comment = (
            organization_comment.contents[1].strip() if organization_comment else ""
        )

        request_regdate = soup.select_one("div.current_problem_regdate")
        request_regdate = request_regdate.contents[1].strip() if request_regdate else ""

        request_moddate = soup.select_one("div.current_problem_moddate")
        request_moddate = request_moddate.contents[1].strip() if request_moddate else ""

        rating = soup.find("input", {"id": "P35_RATING"})
        rating = rating.get("value") if rating else None

        address = soup.select_one("span.current_problem_address")
        address = address.contents[0].replace("\n", " ").strip() if address else ""

        return {
            "status": request_status,
            "status_date": request_status_date,
            "user_comment": user_comment,
            "organization_comment": organization_comment,
            "request_regdate": request_regdate,
            "request_moddate": request_moddate,
            "rating": rating,
            "address": address,
        }

    def fetch_ticket_info(self, ticket: dict) -> dict:
        """
        Fetches the HTML of a ticket page and extracts relevant data.

        Args:
            ticket (dict): A dictionary containing the link to a ticket page.

        Returns:
            dict: A dictionary containing the extracted data
        """
        ticket_url = ticket["request_link"]
        r = self.session.get(url=ticket_url)
        return self.parse_ticket_html(r.text)

    def get_amended_tickets(self, tickets: List[dict], category: dict) -> List[dict]:
        """
        Amend tickets with ticket data and category.

        Args:
            tickets (List[dict]): A list of tickets to be amended with APL ticket.
            category (dict): A dictionary containing the category of each ticket.

        Returns:
            List[dict]: A list of amended tickets.

        """
        amended_tickets = []

        self.session.headers.update(set_apls_headers(self.cookies))
        for ticket in tqdm(tickets):
            apl = self.fetch_ticket_info(ticket)
            del ticket["request_link"]

            amended_ticket = {**ticket, **apl, **category}
            amended_tickets.append(amended_ticket)

        return amended_tickets

    def extract_ticket_info(self, infotext: str) -> Dict[str, str]:
        """
        Extract ticket information from the given string.

        Args:
            infotext (str): A string containing ticket information.

        Returns:
            Dict[str, str]: A dictionary containing ticket information.

        """
        number = re.search(TICKET_NUMBER_PATTERN, infotext)
        district = re.search(DISTRICT_PATTERN, infotext)
        malfunction_type = re.search(MALFUNCTION_TYPE_PATTERN, infotext)
        performer = re.search(PERFORMER_PATTERN, infotext)
        link = re.search(LINK_PATTERN, infotext)

        return {
            "number": number.group(1) if number else None,
            "district": district.group(1) if district else None,
            "malfunction_type": malfunction_type.group(1) if malfunction_type else None,
            "performer": performer.group(1) if performer else "",
            "request_link": HOST_URL + link.group(1) if link else None,
        }

    def parse_tickets(self, raw_tickets: dict) -> List[dict]:
        """
        Parse raw ticket data into a list of ticket dictionaries.

        Args:
            raw_tickets (dict): A dictionary containing raw ticket data.

        Returns:
            List[dict]: A list of ticket dictionaries.

        """
        tickets = []
        for raw_ticket in raw_tickets["row"]:
            infotext = raw_ticket["INFOTEXT"]
            geo_params = raw_ticket["GEOMETRY"]["sdo_point"]

            infotext_params = self.extract_ticket_info(infotext)
            infotext_params.update(geo_params)

            tickets.append(infotext_params)

        return tickets

    def fetch_ticket_data(self, payload: dict) -> List[dict]:
        """
        Fetch ticket data using the given payload.

        Args:
            payload (dict): A dictionary containing request data.

        Returns:
            List[dict]: A list of ticket dictionaries.

        Raises:
            Exception: If the session has expired.

        """
        r = self.session.post(url=AJAX_URL, data=payload)
        ticket_data: list[dict] = r.json()
        if "Your session has expired" in ticket_data.values():
            raise Exception(
                "Your session has expired. You need to update your session params"
            )

        return ticket_data

    def fetch_period_tickets(self, period: str, subjects: dict) -> List[dict]:
        """
        Fetch tickets for the given period and subjects.

        Args:
            period (str): A string representing the period for which to fetch tickets.
            subjects (dict): dict containing the subjects for which to fetch tickets.

        Returns:
            List[dict]: A list of ticket dictionaries.

        """
        payloads = [
            set_ticket_payload(
                protected=self.protected,
                salt=self.salt,
                p_instance=self.p_instance,
                p_request=self.p_request,
                period=period,
                subject=subject,
            )
            for subject in subjects
        ]

        tickets_for_period: List[dict] = []
        self.session.headers.update(self.ticket_headers)
        for subject, payload in zip(subjects, payloads):
            ticket_data = self.fetch_ticket_data(payload)
            ticket_content = self.parse_tickets(ticket_data)
            category = {"category": subjects[subject]}
            amended_apls = self.get_amended_tickets(ticket_content, category)
            tickets_for_period.append(amended_apls)

        return tickets_for_period

    def parse(self, periods: list, subjects: dict) -> None:
        """
        Parse ticket data for the given periods and subjects.

        Args:
            periods (list): representing the periods for which to parse data.
            subjects (dict): dict containing the subjects for which to parse data.

        """
        self.ticket_headers = set_ticket_headers(self.cookies)
        for period in tqdm(periods):
            data = self.fetch_period_tickets(period, subjects)
            self.dump_to_file(data=data, period=period)

    def dump_to_file(self, data: List[dict], period: str) -> None:
        """
        Dump ticket data to a file.

        Args:
            data (List[dict]): A list of ticket dictionaries.
            period (str): str representing the period for which the data is being dumped

        """
        filename = ParserSession.generate_filename(period=period)
        path = f"./data/{filename}"
        with open(path, "w+", encoding="utf8") as f:
            json.dump(data, f, ensure_ascii=False)
