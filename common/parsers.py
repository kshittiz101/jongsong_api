from rest_framework.parsers import JSONParser


class PlainTextJSONParser(JSONParser):
    """
    Accept bodies sent as Content-Type: text/plain that contain JSON.
    Tools like Postman often default raw body to Text instead of JSON.
    """

    media_type = "text/plain"
