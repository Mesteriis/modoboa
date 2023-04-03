"""MX records storage."""

import datetime

from django.db import models
from django.utils import timezone

from modoboa.parameters import tools as param_tools


class MXRecordQuerySet(models.QuerySet):
    """Custom manager for MXRecord."""

    def has_valids(self):
        """Return managed results."""
        if param_tools.get_global_parameter("valid_mxs").strip():
            return self.filter(managed=True).exists()
        return self.exists()


class MXRecordManager(models.Manager):
    """Custom manager for MXRecord."""

    def get_or_create_for_domain(self, domain, ttl=7200):
        """Get or create MX record(s) for given domain.

        DNS queries are not performed while `ttl` (in seconds) is still valid.
        """
        from .. import lib

        now = timezone.now()
        records = self.get_queryset().filter(
            domain=domain, updated__gt=now)
        if records.exists():
            yield from records
            return

        self.get_queryset().filter(domain=domain).delete()

        delta = datetime.timedelta(seconds=ttl)
        domain_mxs = lib.get_domain_mx_list(domain.name)
        if len(domain_mxs) == 0:
            return
        for mx_addr, mx_ip_addr in domain_mxs:
            yield self.get_queryset().create(
                domain=domain,
                name=f'{mx_addr.strip(".")}',
                address=f"{mx_ip_addr}",
                updated=now + delta,
            )


class MXRecord(models.Model):
    """A model used to store MX records for Domain."""

    domain = models.ForeignKey("admin.Domain", on_delete=models.CASCADE)
    name = models.CharField(max_length=254)
    address = models.GenericIPAddressField()
    managed = models.BooleanField(default=False)
    updated = models.DateTimeField()

    objects: MXRecordManager = MXRecordManager.from_queryset(MXRecordQuerySet)()

    def is_managed(self):
        return (
            bool(param_tools.get_global_parameter("valid_mxs").strip())
            if param_tools.get_global_parameter("enable_mx_checks")
            else False
        )

    def __str__(self):
        return "{0.name} ({0.address}) for {0.domain} ".format(self)


class DNSBLQuerySet(models.QuerySet):
    """Custom manager for DNSBLResultManager."""

    def blacklisted(self):
        """Return blacklisted results."""
        return self.exclude(status="")


class DNSBLResult(models.Model):
    """Store a DNSBL query result."""

    domain = models.ForeignKey("admin.Domain", on_delete=models.CASCADE)
    provider = models.CharField(max_length=254, db_index=True)
    mx = models.ForeignKey(MXRecord, on_delete=models.CASCADE)
    status = models.CharField(max_length=45, blank=True, db_index=True)

    objects = models.Manager.from_queryset(DNSBLQuerySet)()

    class Meta:
        app_label = "admin"
        unique_together = [("domain", "provider", "mx")]
