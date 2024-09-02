from abc import abstractmethod
from django.utils import timezone
from payme.constants import *
from payme.exceptions import OrderNotFoundException, InvalidAmountException
from payme.models import TransactionModel
from django.conf import settings

INTEGRATION = settings.PAYME_SETTINGS.get("INTEGRATION_INTEND")

# Settings check
assert INTEGRATION in ('web', 'mobile'), 'must be either web or mobile'


class BaseMerchantValidationClass:
    """
        BaseMerchantValidationClass provides the base implementation for handling various
        payment-related operations in an integrated system.

        This class defines core methods for:
        1. Validating and performing transactions (e.g., check_perform_transaction,
           create_transaction, perform_transaction, check_transaction, cancel_transaction).
        2. Generating statements (get_statement) for transactions over a specified period.
        3. Handling abstract methods (check_order, successful_payment, cancel_payment) that
           need to be implemented by subclasses.
        4. Replying with specific responses based on the transaction's state (reply_order_found,
           reply_order_not_found, reply_invalid_amount, reply_response_check_transaction).

        Attributes:
            ORDER_FOUND (int): Status code for a found order.
            ORDER_NOT_FOND (int): Status code for a not found order.
            INVALID_AMOUNT (int): Status code for an invalid transaction amount.
            METHOD_MAP (dict): Maps methods to their corresponding transaction handlers.

        Methods:
            invoke(method, data): Executes a method corresponding to a transaction operation.
            check_order(amount, account, *args, **kwargs): Validates if the order exists.
            successful_payment(account, transaction, *args, **kwargs): Handles successful payment operations.
            cancel_payment(account, transaction, *args, **kwargs): Handles payment cancellations.
        """

    ORDER_FOUND = 200
    ORDER_NOT_FOND = -31050
    INVALID_AMOUNT = -31001

    def __init__(self):
        self.METHOD_MAP = {
            Methods.check_perform: self.check_perform_transaction,
            Methods.create: self.create_transaction,
            Methods.perform: self.perform_transaction,
            Methods.check: self.check_transaction,
            Methods.cancel: self.cancel_transaction,
            Methods.get_statement: self.get_statement,
        }

        self.reply = None

    def invoke(self, method, data):
        """
        Executes a method corresponding to a transaction operation.
        """
        self.METHOD_MAP[method](data)  # noqa

    @abstractmethod
    def check_order(self, amount, account, *args, **kwargs):
        """
        Validates if the order exists.
        """
        pass

    @abstractmethod
    def successful_payment(self, account, transaction, *args, **kwargs):
        """
        Handles successful payment operations.
        """
        pass

    @abstractmethod
    def cancel_payment(self, account, transaction, *args, **kwargs):
        """
        Handles payment cancellations.
        """
        pass

    def check_perform_transaction(self, validated_data):
        """
        Checks if the transaction can be performed.

        References:
            Documentation: https://developer.help.paycom.uz/metody-merchant-api/checktransaction
        """
        try:
            self.check_order(**validated_data["params"])
        except OrderNotFoundException:
            self.reply_order_not_found(validated_data)
        except InvalidAmountException:
            self.reply_invalid_amount(validated_data)
        else:
            self.reply_order_found()

    def create_transaction(self, validated_data):
        """
        Creates a new transaction or returns an existing one if in progress.

        References:
            Documentation: https://developer.help.paycom.uz/metody-merchant-api/createtransaction
        """
        account = validated_data["params"]["account"]
        try:
            self.check_order(**validated_data["params"])
        except OrderNotFoundException:
            self.reply_order_not_found(validated_data)
            return
        except InvalidAmountException:
            self.reply_invalid_amount(validated_data)
            return

        transaction_id = validated_data["params"]["id"]
        target = {'account': account}

        if INTEGRATION == 'mobile':
            target['transaction_id'] = transaction_id

        tr = TransactionModel.objects.filter(**target, status=TransactionModel.PROCESSING).order_by("-pk")

        if tr.exists():
            tr = tr.first()
            if (
                tr.status != TransactionModel.CANCELED
                and tr.transaction_id == transaction_id
            ):
                self.reply = {
                    "result": {
                        "create_time": int(tr.created_at),
                        "transaction": str(tr.pk),
                        "state": States.create,
                    }
                }

            elif tr.status == TransactionModel.PROCESSING:
                self.reply = {
                    "id": validated_data["id"],
                    "error": {
                        "code": ResponseStatusCodes.in_progress,
                        "message": Messages.transaction["in_progress"],
                    },
                }

            else:
                self.reply = {
                    "id": validated_data["id"],
                    "error": {
                        "code": ResponseStatusCodes.in_progress,
                        "message": Messages.transaction["in_progress"],
                    },
                }
        else:
            now = int(round(timezone.localtime().timestamp()) * 1000)
            tr = TransactionModel.objects.create(
                request_id=validated_data["id"],
                transaction_id=validated_data["params"]["id"],
                amount=validated_data["params"]["amount"] / 100,
                account=validated_data["params"]["account"],
                state=States.create,
                created_at=now,
            )
            self.reply = {
                "result": {
                    "create_time": int(tr.created_at),
                    "transaction": str(tr.pk),
                    "state": States.create,
                }
            }

    def perform_transaction(self, validated_data):
        """
        Performs the transaction if it exists and is not canceled.

        References:
            Documentation: https://developer.help.paycom.uz/metody-merchant-api/performtransaction
        """
        transaction_id = validated_data["params"]["id"]
        request_id = validated_data["id"]
        try:
            obj = TransactionModel.objects.get(transaction_id=transaction_id)

            if obj.state != States.cancel:
                obj.state = States.close
                obj.status = TransactionModel.SUCCESS

                if not obj.performed_at:
                    obj.performed_at = int(round(timezone.localtime().timestamp()) * 1000)
                    self.successful_payment(validated_data["params"], obj)

                self.reply = {
                    "result": {
                        "transaction": str(obj.pk),
                        "perform_time": int(obj.performed_at),
                        "state": States.close,
                    }
                }

            else:
                obj.status = TransactionModel.FAILED

                self.reply = {
                    "error": {
                        "id": request_id,
                        "code": ResponseStatusCodes.unable_to_perform_transaction,
                        "message": Messages.operation["unable_to_perform"],
                    }
                }

            obj.save()
        except TransactionModel.DoesNotExist:
            self.reply = {
                "error": {
                    "id": request_id,
                    "code": ResponseStatusCodes.transaction_not_found,
                    "message": Messages.transaction["not_found"],
                }
            }

    def check_transaction(self, validated_data):
        """
        Checks the status of a transaction.

        References:
            Documentation: https://developer.help.paycom.uz/metody-merchant-api/checkperformtransaction
        """
        transaction_id = validated_data["params"]["id"]
        request_id = validated_data["id"]

        try:
            transaction = TransactionModel.objects.get(transaction_id=transaction_id)
            self.reply_response_check_transaction(transaction)
        except TransactionModel.DoesNotExist:
            self.reply = {
                "error": {
                    "id": request_id,
                    "code": ResponseStatusCodes.transaction_not_found,
                    "message": Messages.transaction["not_found"],
                }
            }

    def cancel_transaction(self, validated_data):
        """
        Cancels the transaction if it is in a cancellable state.

        References:
            Documentation: https://developer.help.paycom.uz/metody-merchant-api/canceltransaction
        """
        transaction_id = validated_data["params"]["id"]
        reason = validated_data["params"]["reason"]
        request_id = validated_data["id"]

        try:
            tr = TransactionModel.objects.get(transaction_id=transaction_id)

            if tr.state == 1:
                tr.state = States.cancel
            elif tr.state == 2:
                tr.state = States.perform_canceled
                self.cancel_payment(validated_data["params"], tr)

            tr.reason = reason
            tr.status = TransactionModel.CANCELED

            now = timezone.localtime()

            if not tr.canceled_at:
                tr.canceled_at = int(round(now.timestamp()) * 1000)
            tr.save()

            self.reply_response_check_transaction(tr)
        except TransactionModel.DoesNotExist:
            self.reply = {
                "error": {
                    "id": request_id,
                    "code": ResponseStatusCodes.transaction_not_found,
                    "message": Messages.transaction["not_found"],
                }
            }

    def get_statement(self, validated_data):
        """
        Generates a statement for transactions over a specified period.

        References:
            Documentation: https://developer.help.paycom.uz/metody-merchant-api/getstatement
        """
        from_datetime = validated_data.get("params").get("from")
        to_datetime = validated_data.get("params").get("to")

        transactions = TransactionModel.objects.filter(
            created_at__gte=from_datetime, created_at__lte=to_datetime
        )

        transactions = [
            {
                "id": tr.transaction_id,
                "time": int(tr.created_at),
                "amount": tr.amount,
                "account": {
                    "account": tr.account,
                },
                "create_time": int(tr.created_at) if tr.created_at else 0,
                "perform_time": int(tr.performed_at) if tr.performed_at else 0,
                "cancel_time": int(tr.canceled_at) if tr.canceled_at else 0,
                "transaction": tr.request_id,
                "state": tr.state,
                "reason": tr.reason,
            }
            for tr in transactions
        ]

        self.reply = {"result": {"transactions": transactions}}

    def reply_order_found(self):
        """
        Replies with an order found response.
        """
        self.reply = {"result": {"allow": True}}

    def reply_order_not_found(self, validated_data):
        """
        Replies with an order not found error.
        """

        self.reply = {
            "error": {
                "id": validated_data["id"],
                "code": ResponseStatusCodes.order_not_found,
                "message": Messages.order["not_found"],
            }
        }

    def reply_invalid_amount(self, validated_data):
        """
        Replies with an invalid amount error.
        """
        self.reply = {
            "error": {
                "id": validated_data["id"],
                "code": ResponseStatusCodes.invalid_amount,
                "message": Messages.order["invalid_amount"],
            }
        }

    def reply_response_check_transaction(self, transaction: TransactionModel):
        """
        Replies with the transaction status response.
        """
        self.reply = {
            "result": {
                "create_time": (
                    int(transaction.created_at) if transaction.created_at else 0
                ),
                "perform_time": (
                    int(transaction.performed_at) if transaction.performed_at else 0
                ),
                "cancel_time": (
                    int(transaction.canceled_at) if transaction.canceled_at else 0
                ),
                "transaction": str(transaction.id),
                "state": transaction.state,
                "reason": transaction.reason,
            }
        }
