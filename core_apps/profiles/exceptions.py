from rest_framework.exceptions import APIException


class NotYourProfile(APIException):
    status_code = 403
    default_detail = "you can't edit a profile that doens't belong to you!"


class CantFollowYourself(APIException):
    status_code = 403
    default_detail = "you can't follow yourself!"