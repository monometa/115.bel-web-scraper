# 115.bel web scraper

![image](https://user-images.githubusercontent.com/107945681/207574269-61ec5140-e69e-4df4-941b-5459fbb3dedf.png)

This is a https://115.xn--90ais/ python web scraper automated using Github actions that receives raw data for the previous month and stores it in S3 bucket as JSON. Historical raw data by month available from 2019. 

Dataset language: Russian

Actual and processed dataset is available at [kaggle](https://www.kaggle.com/datasets/illiakaltovich/115bel).

## Files and What They Do

| Name | Description |
| - | - |
| [`start_parser.yml`](.github/workflows/start_parser.yml) | A Github action to automate the collection and storage of data |
| [`get_data.py`](/get_data.py) | A Python script to start parsing (by default, parsing data for the previous month)  |
| [`parser.py`](/parser.py) | A Python script that contains two main classes for parsing: Parser and ParserConfig |
| [`parser_config.py`](/parser_config.py) | A Python script that stores auxiliary dictionaries for configuration and a list of categories for parsing |
| [`requirements.txt`](/requirements.txt) | A file that contains Python package dependencies used in this project |

## Raw request example

```
         {
            "number": "2047.10.061022",
            "district": "Минск",
            "malfunction_type": "Не вывезен крупногабаритный мусор",
            "performer": "ЖЭС №19 ЖЭУ №3 Первомайского р-на г. Минска",
            "x": "3074687.33640699",
            "y": "7156835.94369358",
            "z": "null",
            "status": "Заявка закрыта",
            "status_date": "Выполнено 07.10.2022",
            "user_comment": "Не вывезен крупногабаритный мусор",
            "organization_comment": "Выполнена уборка контейнерной площадки.",
            "request_regdate": "06.10.2022 07:07",
            "request_moddate": "07.10.2022 13:25",
            "rating": null,
            "address": "Минск, Первомайский район, улица Кедышко, 12Б",
            "category": "Обращение с ТКО"
        }
```
