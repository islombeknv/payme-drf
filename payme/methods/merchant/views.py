from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from payme.auth import authentication
from payme.constants import Messages
from payme.methods.merchant.serializers import PaymeSerializer
from payme.methods.merchant.validation_classes import BaseMerchantValidationClass


class BaseMerchantAPIView(APIView):
    """
    API view for handling Payme transactions.

    This view handles incoming POST requests to process transactions through
    the Payme system. It uses custom authentication and validation classes
    to ensure secure and valid transactions.
    """

    validation_class = BaseMerchantValidationClass
    authentication_classes = []
    permission_classes = [AllowAny]
    renderer_classes = [JSONRenderer]

    def post(self, request):
        """
        Handle POST request for Payme transactions.

        Args:
            request (Request): The request object containing the data.

        Returns:
            Response: A response object with the transaction result or error message.
        """
        auth = authentication(request)

        if not auth:
            return Response(Messages.auth["error"])

        serializer = PaymeSerializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)

        method = serializer.validated_data["method"]
        validator = self.validation_class()
        validator.invoke(method, serializer.validated_data)

        return Response(validator.reply)

