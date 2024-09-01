from django.db import models
from django.utils.translation import gettext_lazy as _


class TransactionModel(models.Model):
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELED = "canceled"
    STATUS = (
        (PROCESSING, _("Processing")),
        (SUCCESS, _("Success")),
        (FAILED, _("Failed")),
        (CANCELED, _("Canceled")),
    )

    transaction_id = models.CharField(max_length=255)
    request_id = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    state = models.IntegerField(blank=True, null=True)
    status = models.CharField(choices=STATUS, default=PROCESSING, max_length=55)
    performed_at = models.CharField(null=True, max_length=255)
    canceled_at = models.CharField(null=True, max_length=255)
    created_at = models.CharField(null=True, max_length=255)
    reason = models.IntegerField(null=True)
    account = models.JSONField(null=True)

    def __str__(self):
        return self.transaction_id

    class Meta:
        verbose_name = _("Payme transaction")
        verbose_name_plural = _("Payme transactions")
