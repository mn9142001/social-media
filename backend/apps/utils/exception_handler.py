from rest_framework.views import exception_handler
from rest_framework.exceptions import ErrorDetail, APIException
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from rest_framework.response import Response

def translate(message : ErrorDetail):

    data = {}

    with translation.override("ar"):
        ar = str(_(message))
        data = {
            "en" : str(message),
            "ar" : ar
        }
        return data 


def extract_detail(detail, key=None):

    if isinstance(detail, dict):
        data = {}

        for k, v in detail.items():
            data[k] = extract_detail(v, key=k)

        return data

    elif isinstance(detail, list):
        for err in detail:
            if not err: continue
            return extract_detail(err)

    else:
        return translate(detail)


def handle_detail_exc(exc : APIException, response : Response):
    response.data = extract_detail(exc.detail)
    return response


def api_handler(exc, context):
    response = exception_handler(exc, context)
    if isinstance(exc, APIException):
        return handle_detail_exc(exc, response)
    return response
