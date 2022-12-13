from parser_config import *
import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import date, timedelta
from tqdm import tqdm


class Parser:
    def __init__(
        self, session, cookies, p_instance, p_request, protected, salt
    ) -> None:
        self.s = session
        self.cookies = cookies
        self.p_instance = p_instance
        self.p_request = p_request
        self.protected = protected
        self.salt = salt
        self.ticket_headers = {}

    def set_ticket_headers(self):
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-GB,en-US;q=0.9,en-BY;q=0.8,en;q=0.7,ru;q=0.6",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Cookie": self.cookies,
            "Host": "115.xn--90ais",
            "Origin": "https://115.xn--90ais",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "sec-ch-ua": '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Linux",
        }
        self.ticket_headers = headers

    def set_ticket_payload(self, period="", subject="") -> dict:

        payload_json_params = {
            "pageItems": {
                "itemsToSubmit": [
                    {"n": "P19_PERIOD", "v": period},
                    {"n": "P19_SUBJECT", "v": subject},
                ],
                "protected": self.protected,
                "rowVersion": "",
            },
            "salt": self.salt,
        }

        payload = {
            "p_flow_id": "10901",
            "p_flow_step_id": "19",
            "p_instance": self.p_instance,
            "p_debug": "",
            "p_request": self.p_request,
            "x01": "3857",
            "x02": "3103495265163666",
            "x03": "7141386464106095",
            "x04": "3150255616417175",
            "x05": "7210179788385880",
            "x06": "N",
            "x07": "11",
            "x10": "FOIDATA",
            "p_json": payload_json_params,
        }

        payload["p_json"] = json.dumps(payload["p_json"])

        return payload

    def get_ticket_content(self, raw_tickets):
        tickets = []
        for raw_ticket in raw_tickets["row"]:

            infotext = raw_ticket["INFOTEXT"]
            geo_params = raw_ticket["GEOMETRY"]["sdo_point"]

            infotext_params = self.retrieve_infotext_data(infotext)
            infotext_params.update(geo_params)
            tickets.append(infotext_params)

        return tickets

    def retrieve_infotext_data(self, infotext):

        link_host = "https://115.xn--90ais/portal/"
        try:
            number = re.search("Заявка № (.*?)<br>", infotext).group(1)
        except AttributeError:
            number = None
        try:
            district = re.search("Адрес: </b>(.*?),", infotext).group(1)
        except AttributeError:
            district = None
        try:
            malfunction_type = re.search(
                "Вид неисправности: </b>(.*?)<br>", infotext
            ).group(1)
        except AttributeError:
            malfunction_type = None
        try:
            performer = re.search("<b> Исполнитель: </b>(.*?)<br>", infotext).group(1)
        except AttributeError:
            performer = ""
        link = link_host + re.search('<a href="(.*?)">', infotext).group(1)

        lst = {
            "number": number,
            "district": district,
            "malfunction_type": malfunction_type,
            "performer": performer,
            "request_link": link,
        }

        return lst

    def fetch_raw_tickets(self, payload):
        self.s.headers.update(self.ticket_headers)
        r = self.s.post(url=post_url, data=payload)
        raw_tickets = r.json()
        if "Your session has expired" in raw_tickets.values():
            raise Exception(
                "Your session has expired. You need to update your session params"
            )

        return raw_tickets

    def set_apls_headers(self) -> dict:
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-GB,en-US;q=0.9,en-BY;q=0.8,en;q=0.7,ru;q=0.6",
            "Connection": "keep-alive",
            "Cookie": self.cookies,
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "sec-ch-ua": '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Linux",
        }

        return headers

    def fetch_apl(self, url, cookies, referer):

        headers = self.set_apls_headers(cookies=cookies, referer=referer)
        self.s.headers.update(headers)

        r = self.s.get(url=url, headers=headers)

        request_description = self.retrieve_apl_data(r.text)

        return request_description

    def retrieve_apl_data(self, html_doc):

        soup = BeautifulSoup(html_doc, "html.parser")

        try:
            request_status = (
                soup.select_one("div.current_problem_status > span").contents[0].strip()
            )
        except AttributeError:
            request_status = ""
        try:
            request_status_date = (
                soup.select_one("div.current_problem_status_date").contents[0].strip()
            )
        except AttributeError:
            request_status_date = ""
        try:
            user_comment = (
                soup.select_one("div.t-Region-body > div:nth-child(2)")
                .contents[1]
                .replace("\r", "")
                .replace("\n", " ")
                .strip()
            )
        except AttributeError:
            user_comment = ""
        organization_comment = (
            soup.select_one("div.t-Region-body > div:nth-child(3)").contents[1].strip()
        )
        request_regdate = (
            soup.select_one("div.current_problem_regdate").contents[1].strip()
        )
        request_moddate = (
            soup.select_one("div.current_problem_moddate").contents[1].strip()
        )
        try:
            rating = soup.find("input", {"id": "P35_RATING"}).get("value")
        except AttributeError:
            rating = None
        adress = (
            soup.select_one("span.current_problem_address ")
            .contents[0]
            .replace("\n", " ")
            .strip()
        )

        request_description = {
            "status": request_status,
            "status_date": request_status_date,
            "user_comment": user_comment,
            "organization_comment": organization_comment,
            "request_regdate": request_regdate,
            "request_moddate": request_moddate,
            "rating": rating,
            "address": adress,
        }

        return request_description

    def dump_to_file(self, data, period):
        filename = ParserConfig.generate_filename(period=period)
        path = f"./data/{filename}"
        with open(path, "w+", encoding="utf8") as f:
            json.dump(data, f, ensure_ascii=False)

    def fetch_period_data(self, period, subjects):
        period_data = []

        for subject in tqdm(subjects):
            category_param = {"category": subjects[subject]}
            payload = self.set_ticket_payload(period, subject)

            raw_tickets = self.fetch_raw_tickets(payload)
            tickets = self.get_ticket_content(raw_tickets)
            amended_apls = self.get_amended_apls(tickets, category_param)

            period_data.append(amended_apls)
        return period_data

    def fetch_apls(self, ticket):
        apl_url = ticket["request_link"]
        apl_headers = self.set_apls_headers()
        self.s.headers.update(apl_headers)
        r = self.s.get(url=apl_url)
        apl = self.retrieve_apl_data(r.text)
        return apl

    def get_amended_apls(self, tickets, category_param):

        db = []
        for ticket in tqdm(tickets):
            apl = self.fetch_apls(ticket=ticket)
            del ticket["request_link"]

            amended_apl = {**ticket, **apl, **category_param}
            db.append(amended_apl)

        return db

    def parse(self, periods, subjects):
        self.set_ticket_headers()
        for period in tqdm(periods):
            data = self.fetch_period_data(period, subjects)
            self.dump_to_file(data=data, period=period)


class ParserConfig:
    def __init__(self) -> None:
        self.s = requests.Session()
        self.cookies = ""

    def get_current_session(self):
        return self.s

    def get_cookies(self):
        return self.cookies

    def set_cookies(self, cookiesJar) -> None:
        cookies_dict = requests.utils.dict_from_cookiejar(cookiesJar)
        cookies = f'ORA_WWV_APP_10901={cookies_dict["ORA_WWV_APP_10901"]}; ORA_WWV_RAC_INSTANCE=2'
        self.cookies = cookies

    def get_url_map(self, response_text) -> str:
        soup = BeautifulSoup(response_text, "html.parser")
        a_map_tag = soup.select_one(
            "div.t-NavigationBar-menu > ul > li:nth-child(1) > a[href]"
        )
        url_map_sub = a_map_tag["href"]
        url_map = host_url + url_map_sub
        return url_map

    def retrieve_payload_params(self, response_text) -> dict:
        soup = BeautifulSoup(response_text, "html.parser")

        protected = soup.find("input", {"id": "pPageItemsProtected"}).get("value")
        p_instance = soup.find("input", {"id": "pInstance"}).get("value")
        salt = soup.find("input", {"id": "pSalt"}).get("value")
        js_obj = soup.find_all("script", type="text/javascript")[3].string
        p_request_value = re.search('\{createPluginMap\(".*?","(.*?)","', js_obj).group(
            1
        )
        p_request = "PLUGIN=" + p_request_value
        payload_params = {
            "p_instance": p_instance,
            "p_request": p_request,
            "protected": protected,
            "salt": salt,
        }

        return payload_params

    def fetch_payload_params(self, url_map: str) -> dict:
        r = self.s.get(url=url_map)
        payload_params = self.retrieve_payload_params(r.text)
        return payload_params

    def get_payload_params(self) -> dict:
        r = self.s.get(url=entrypoint_url)
        self.set_cookies(r.cookies)
        url_map = self.get_url_map(r.text)
        payload_params = self.fetch_payload_params(url_map)

        return payload_params

    def generate_filename(period: str) -> str:
        """
        Generate filename for dump json for current period
        """
        ru_month = re.search(f", 01 (.*?), ", period).group(1)
        year = period[-4:]

        for key, value in months_translate.items():
            if ru_month == value:
                eng_month = key

        filename = f"{year}_{eng_month.lower()}.json"
        return filename

    def generate_template_date(input_datetime):
        """
        Generate formatted date in Russian Language
        """
        first_day_month_current = input_datetime.replace(day=1)
        previous_month = first_day_month_current - timedelta(days=1)
        first_day_previous_month = previous_month.replace(day=1)
        date_string = first_day_previous_month.strftime("%w, %d %B, %Y")

        # change day of week from number to ru_name
        day_number = re.search("(.*?),", date_string).group(1)
        date_string = date_string.replace(day_number, week_days[day_number], 1)

        # change month name from eng to ru
        for key in months_translate.keys():
            date_string = date_string.replace(key, months_translate[key])

        return date_string
