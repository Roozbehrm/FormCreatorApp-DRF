from asgiref.sync import async_to_sync
from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Answer, AnswerOption, Field, FieldOption, Form, Submission


def _invalidate_form_and_process(form_id, process_run_id=None):
    from apps.core.cache import form_report_key, invalidate_form, invalidate_process
    from apps.processes.models import ProcessStep, ProcessRun

    try:
        form = Form.objects.only("id", "uuid").get(id=form_id)
    except Form.DoesNotExist:
        from django.core.cache import cache

        cache.delete(form_report_key(form_id))
    else:
        invalidate_form(form.id, form.uuid)

    process_ids = set(
        ProcessStep.objects.filter(form_id=form_id).values_list("process_id", flat=True)
    )
    if process_run_id:
        process_id = (
            ProcessRun.objects.filter(id=process_run_id)
            .values_list("process_id", flat=True)
            .first()
        )
        if process_id:
            process_ids.add(process_id)

    for process_id in process_ids:
        invalidate_process(process_id)


def _notify_realtime(form_id):
    def send():
        try:
            from apps.forms.models import Form
            from apps.reports.services import form_report
            from channels.layers import get_channel_layer

            form = Form.objects.get(id=form_id)
            channel_layer = get_channel_layer()
            if channel_layer is None:
                return
            async_to_sync(channel_layer.group_send)(
                f"report.form.{form.uuid}",
                {"type": "report.update", "payload": form_report(form)},
            )
        except Exception:
            # Realtime reporting is optional and must never break a DB transaction.
            return

    transaction.on_commit(send)


def _submission_context(submission_id):
    return Submission.objects.filter(id=submission_id).values(
        "form_id", "process_run_id"
    ).first()


@receiver(post_save, sender=Form)
def form_saved(sender, instance, **kwargs):
    _invalidate_form_and_process(instance.id)


@receiver(post_delete, sender=Form)
def form_deleted(sender, instance, **kwargs):
    from apps.core.cache import invalidate_form

    invalidate_form(instance.id, instance.uuid)


@receiver(post_save, sender=Submission)
def submission_saved(sender, instance, **kwargs):
    _invalidate_form_and_process(instance.form_id, instance.process_run_id)
    if instance.is_complete:
        _notify_realtime(instance.form_id)


@receiver(post_delete, sender=Submission)
def submission_deleted(sender, instance, **kwargs):
    _invalidate_form_and_process(instance.form_id, instance.process_run_id)


@receiver(post_save, sender=Answer)
def answer_saved(sender, instance, **kwargs):
    context = _submission_context(instance.submission_id)
    if context:
        _invalidate_form_and_process(context["form_id"], context["process_run_id"])


@receiver(post_delete, sender=Answer)
def answer_deleted(sender, instance, **kwargs):
    context = _submission_context(instance.submission_id)
    if context:
        _invalidate_form_and_process(context["form_id"], context["process_run_id"])


def _answer_context(answer_id):
    return Answer.objects.filter(id=answer_id).values_list("submission_id", flat=True).first()


@receiver(post_save, sender=AnswerOption)
def answer_option_saved(sender, instance, **kwargs):
    submission_id = _answer_context(instance.answer_id)
    if submission_id:
        context = _submission_context(submission_id)
        if context:
            _invalidate_form_and_process(context["form_id"], context["process_run_id"])


@receiver(post_delete, sender=AnswerOption)
def answer_option_deleted(sender, instance, **kwargs):
    submission_id = _answer_context(instance.answer_id)
    if submission_id:
        context = _submission_context(submission_id)
        if context:
            _invalidate_form_and_process(context["form_id"], context["process_run_id"])


@receiver(post_save, sender=Field)
def field_saved(sender, instance, **kwargs):
    _invalidate_form_and_process(instance.form_id)


@receiver(post_delete, sender=Field)
def field_deleted(sender, instance, **kwargs):
    _invalidate_form_and_process(instance.form_id)


@receiver(post_save, sender=FieldOption)
def field_option_saved(sender, instance, **kwargs):
    _invalidate_form_and_process(instance.field.form_id)


@receiver(post_delete, sender=FieldOption)
def field_option_deleted(sender, instance, **kwargs):
    from apps.forms.models import Field

    form_id = Field.objects.filter(id=instance.field_id).values_list("form_id", flat=True).first()
    if form_id:
        _invalidate_form_and_process(form_id)
