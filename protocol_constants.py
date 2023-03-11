# ruff: disable=line-too-long
import json


def set_apls_headers(cookies) -> dict:
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",  # noqa: E501
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-GB,en-US;q=0.9,en-BY;q=0.8,en;q=0.7,ru;q=0.6",
        "Connection": "keep-alive",
        "Cookie": cookies,
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",  # noqa: E501
        "X-Requested-With": "XMLHttpRequest",
        "sec-ch-ua": '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',  # noqa: E501
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Linux",
    }

    return headers


def set_ticket_headers(cookies) -> None:
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-GB,en-US;q=0.9,en-BY;q=0.8,en;q=0.7,ru;q=0.6",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie": cookies,
        "Host": "115.xn--90ais",
        "Origin": "https://115.xn--90ais",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",  # noqa: E501
        "X-Requested-With": "XMLHttpRequest",
        "sec-ch-ua": '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',  # noqa: E501
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Linux",
    }
    return headers


def set_ticket_payload(
    protected: str,
    salt: str,
    p_instance: str,
    p_request,
    period: str = "",
    subject: str = "",
) -> dict:
    payload_json_params = {
        "pageItems": {
            "itemsToSubmit": [
                {"n": "P19_PERIOD", "v": period},
                {"n": "P19_SUBJECT", "v": subject},
            ],
            "protected": protected,
            "rowVersion": "",
        },
        "salt": salt,
    }

    payload = {
        "p_flow_id": "10901",
        "p_flow_step_id": "19",
        "p_instance": p_instance,
        "p_debug": "",
        "p_request": p_request,
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
