from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from payme.auth import authentication
from payme.constants import Messages
from payme.methods.merchant.serializers import PaymeSerializer
from payme.methods.merchant.validation_classes import BaseMerchantValidationClass


class BaseMerchantAPIView(APIView):
    validation_class = BaseMerchantValidationClass
    authentication_classes = []
    permission_classes = [AllowAny]
    renderer_classes = [JSONRenderer]

    def post(self, request):
        auth = authentication(request)

        if auth is False or not auth:
            return Response(Messages.auth["error"])

        serializer = PaymeSerializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)

        method = serializer.validated_data["method"]
        validator = self.validation_class()
        validator.invoke(method, serializer.validated_data)

        return Response(validator.reply)
