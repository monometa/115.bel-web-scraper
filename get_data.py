from parser_config import *
from parser import ParserConfig, Parser
from datetime import date

def main():

    config = ParserConfig()
    payload_params = config.get_payload_params()
    cookies = config.get_cookies()
    session = config.get_current_session()

    parser_session = Parser(
        session = session,
        cookies = cookies,
        p_instance = payload_params['p_instance'],
        p_request = payload_params['p_request'],
        protected = payload_params['protected'],
        salt = payload_params['salt'],
    )
    periods = []
    periods.append(ParserConfig.generate_template_date(date.today()))
    parser_session.parse(periods=periods, subjects=subjects)

if __name__ == "__main__":
    main()
