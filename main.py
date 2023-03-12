from datetime import date
from parser import Parser, ParserSession

from logs.set_logger import logger
from parser_config import get_configured_subjects


def main() -> None:
    logger.info("Start getting http headers and payload")
    config = ParserSession()
    payload_params = config.get_payload()
    cookies = config.cookies
    session = config.session
    logger.info("Init main parser")
    parser_session = Parser(
        session=session,
        cookies=cookies,
        p_instance=payload_params["p_instance"],
        p_request=payload_params["p_request"],
        protected=payload_params["protected"],
        salt=payload_params["salt"],
    )
    periods = []
    logger.info("Getting periods")
    periods.append(ParserSession.generate_template_date(date.today()))
    logger.info("Getting subjects")
    subjects = get_configured_subjects()
    logger.info("Start parsing")
    parser_session.parse(periods=periods, subjects=subjects)
    logger.info("Finish parsing")


if __name__ == "__main__":
    main()
