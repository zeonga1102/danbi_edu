from rest_framework.permissions import BasePermission
from rest_framework.exceptions import APIException
from rest_framework import status


class GenericAPIException(APIException):
    def __init__(self, status_code, detail=None, code=None):
        self.status_code=status_code
        super().__init__(detail=detail, code=code)


class IsAuthenticatedOrIsReadOnly(BasePermission):

    message = "접근 권한 없음"

    def has_permission(self, request, view):
        if request.method == "GET":
            return True
        
        user = request.user
        if not user.is_authenticated:
            response ={
                    "detail": "로그인 필요",
                }
            raise GenericAPIException(status_code=status.HTTP_401_UNAUTHORIZED, detail=response)

        return True