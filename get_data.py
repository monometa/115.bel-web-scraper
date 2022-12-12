# import re
# import json
# from tqdm import tqdm

# import requests
# from bs4 import BeautifulSoup
from parser_config import *
from parser import ParserConfig, Parser

def main():

    config = ParserConfig()
    payload_params = config.get_payload_params()
    cookies = config.get_cookies()
    session = config.get_current_session()

    # breakpoint()
    parser_session = Parser(
        session = session,
        cookies = cookies,
        p_instance = payload_params['p_instance'],
        p_request = payload_params['p_request'],
        protected = payload_params['protected'],
        salt = payload_params['salt'],
        # **payload_params

    )
    # breakpoint()
    parser_session.parse(periods=periods, subjects=subjects)

if __name__ == "__main__":
    main()
