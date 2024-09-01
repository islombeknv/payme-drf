import base64
from decimal import Decimal
from django.conf import settings

# Define the Kassa ID from the settings
KASSA_ID = settings.PAYME_SETTINGS["KASSA_ID"]


class PaymeHelper:
    """
    Helper class to generate payment initialization URLs for Payme.
    """

    # Base URL for Payme checkout
    LINK = 'https://checkout.paycom.uz'

    def create_initialization(self, amount: Decimal, ac_params: dict, return_url: str) -> str:
        """
        Creates an initialization URL for Payme payment.

        Args:
            amount (Decimal): The amount to be paid.
            ac_params (dict): Additional parameters required for payment (e.g., order_id and etc).
            return_url (str): The URL to redirect after payment completion.

        Returns:
            str: A URL string for initializing the Payme payment.

        Example:
            >>> helper = PaymeHelper()
            >>> helper.create_initialization(
                    amount=Decimal(5000.00),
                    ac_params={"order_id": "12221"},
                    return_url='https://example.com/success/'
                )
        """

        # Construct the `ac` parameters dynamically
        ac_string = ";".join([f"ac.{key}={value}" for key, value in ac_params.items()])

        # Combine all parameters into the final string
        params = f"m={KASSA_ID};{ac_string};a={amount};c={return_url}"
        # Encode the parameters in base64
        encode_params = base64.b64encode(params.encode("utf-8")).decode("utf-8")

        # Return the final payment URL
        return f"{self.LINK}/{encode_params}"
