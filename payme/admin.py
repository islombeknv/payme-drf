from django.contrib import admin

from payme.models import TransactionModel


class TransactionModelAdmin(admin.ModelAdmin):
    list_display = (
        "transaction_id",
        "request_id",
        "amount",
        "state",
        "get_status_display",
        "performed_at",
        "canceled_at",
        "created_at",
        "reason",
    )
    list_filter = ("status",)
    search_fields = [
        "transaction_id",
        "request_id",
        "status",
        "performed_at",
        "canceled_at",
        "created_at",
        "reason",
    ]


admin.site.register(TransactionModel, TransactionModelAdmin)
