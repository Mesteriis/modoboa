"""Transport handlers."""

from django.db.models import signals
from django.dispatch import receiver

from modoboa.core import signals as core_signals
from . import backends, models, postfix_maps


@receiver(core_signals.register_postfix_maps)
def register_postfix_maps(sender, **kwargs):
    """Register postfix maps."""
    return [
        postfix_maps.TransportMap,
    ]


@receiver(signals.pre_save, sender=models.Transport)
def serialize_transport_settings(sender, instance, **kwargs):
    """Call backend serialize method on transport."""
    if backend := backends.manager.get_backend(instance.service):
        backend.serialize(instance)
