class ResponseStatusCodes:
    order_found = 200
    order_not_found = -31050
    transaction_not_found = -31003
    unable_to_perform_transaction = -31008
    invalid_amount = -31001
    in_progress = -31099


class States:
    create = 1
    close = 2
    cancel = -1
    perform_canceled = -2


class Methods:
    check_perform = "CheckPerformTransaction"
    create = "CreateTransaction"
    perform = "PerformTransaction"
    check = "CheckTransaction"
    cancel = "CancelTransaction"
    get_statement = "GetStatement"


class Messages:
    order = {
        "not_found": {
            "uz": "Buyurtma topilmadi",
            "ru": "Заказ не найден",
            "en": "Order not fond",
        },
        "invalid_amount": {
            "uz": "Miqdori notog'ri",
            "ru": "Неверная сумма",
            "en": "Invalid amount",
        },
    }
    transaction = {
        "not_found": {
            "uz": "Tranzaksiya topilmadi",
            "ru": "Транзакция не найдена",
            "en": "Transaction not found",
        },
        "in_progress": {
            "uz": "Buyurtma to'lo'vi hozirda amalga oshirilmoqda",
            "ru": "Платеж на этот заказ на данный момент в процессе",
            "en": "Payment for this order is currently on process",
        },
    }
    operation = {
        "unable_to_perform": {
            "uz": "Ushbu amalni bajarib bo'lmaydi",
            "ru": "Невозможно выполнить данную операцию",
            "en": "Unable to perform operation",
        }
    }
    auth = {
        "error": {
            "error": {
                "code": -32504,
                "message": {
                    "ru": "пользователь не существует",
                    "uz": "foydalanuvchi mavjud emas",
                    "en": "user does not exist",
                },
                "data": "user does not exist",
            }
        }
    }
