### Requirements
````
pip install django
pip install djangorestframework
pip install payme-drf 
pip install requests

# supported versions
python 3.5 +
django 2 +
djangorestframework 3.7 +
payme-drf 0.01 +
````

**settings.py**

```python
PAYME_SETTINGS = {
    "KASSA_ID": "",
    "SECRET_KEY": "",
    "TOKEN": "",
    "INTEGRATION_INTEND": "" # either web or mobile
}

INSTALLED_APPS = [
    ...
    'rest_framework',
    'payme',
    ...
]
```

```
python manage.py migrate
```

### Create payme user
```python
python manage.py create_payme_user
```

### view.py

```python
from payme.methods.merchant.validation_classes import BaseMerchantValidationClass
from payme.methods.merchant.views import BaseMerchantAPIView

class MerchantValidationClass(BaseMerchantValidationClass):
    """
    MerchantValidationClass implements abstract methods from BaseMerchantValidationClass
    to handle specific payment validation logic.

    Exceptions Handled:
        - OrderNotFoundException: Raised when the order is not found.
        - InvalidAmountException: Raised when the transaction amount is invalid.

    Methods:
        check_order(amount, account, **kwargs): Validates the existence and correctness of the order.
        successful_payment(params, *args, **kwargs): Processes actions for a successful payment.
        cancel_payment(params, *args, **kwargs): Processes actions for canceling a payment.
    """

    def check_order(self, amount, account, **kwargs):
        """Validates the existence and correctness of the order."""
        ...

    def successful_payment(self, params, *args, **kwargs):
        """Processes actions for a successful payment."""
        ...

    def cancel_payment(self, params, *args, **kwargs):
        """Processes actions for canceling a payment."""
        ...


class PaymeMerchantAPIView(BaseMerchantAPIView):
    """
    PaymeMerchantAPIView handles API requests for Payme merchant operations
    by using the MerchantValidationClass to validate transactions.

    Attributes:
        validation_class (type): The validation class used for processing merchant transactions.
    """
    validation_class = MerchantValidationClass
```

### urls.py
```
from django.urls import path

urlpatterns = [
    path('payme/', PaymeMerchantAPIView.as_view())
]
```

### create_initialization.py
https://help.paycom.uz/uz/initsializatsiya-platezhey/otpravka-cheka-po-metodu-get

📌 You can pass multiple items to ac_params to customize the payment request.

```python
from payme.methods.merchant.helpers import PaymeHelper
from decimal import Decimal

helper = PaymeHelper()
ac_params = {"order_id": "12221"} 
url = helper.create_initialization(amount=Decimal(5000.00), ac_params=ac_params, return_url='https://example.com/success/')
print(url)
```
