from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Process, ProcessRun, ProcessStep, StepCompletion


def _invalidate(process_id):
    from apps.core.cache import invalidate_process

    if process_id:
        invalidate_process(process_id)


def _process_id_for_run(run_id):
    return ProcessRun.objects.filter(id=run_id).values_list("process_id", flat=True).first()


@receiver(post_save, sender=Process)
def process_saved(sender, instance, **kwargs):
    _invalidate(instance.id)


@receiver(post_delete, sender=Process)
def process_deleted(sender, instance, **kwargs):
    _invalidate(instance.id)


@receiver(post_save, sender=ProcessStep)
def process_step_saved(sender, instance, **kwargs):
    _invalidate(instance.process_id)


@receiver(post_delete, sender=ProcessStep)
def process_step_deleted(sender, instance, **kwargs):
    _invalidate(instance.process_id)


@receiver(post_save, sender=ProcessRun)
def process_run_saved(sender, instance, **kwargs):
    _invalidate(instance.process_id)


@receiver(post_delete, sender=ProcessRun)
def process_run_deleted(sender, instance, **kwargs):
    _invalidate(instance.process_id)


@receiver(post_save, sender=StepCompletion)
def completion_saved(sender, instance, **kwargs):
    _invalidate(_process_id_for_run(instance.run_id))


@receiver(post_delete, sender=StepCompletion)
def completion_deleted(sender, instance, **kwargs):
    _invalidate(_process_id_for_run(instance.run_id))
