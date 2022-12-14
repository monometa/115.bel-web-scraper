# 115.bel web scraper

This is a https://115.xn--90ais/ python web scraper automated using Github actions. Received raw data is stored in S3 bucket as JSON files divided by months from 2019. 

Dataset language: Russian

Actual and processed dataset is available at [kaggle](https://www.kaggle.com/datasets/illiakaltovich/115bel)

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
