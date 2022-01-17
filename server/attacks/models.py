from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel


class Instance(TimeStampedModel):

    class StatusChoices(models.TextChoices):
        IDLE = 'idle', _('idle')
        RUNNING_TEST = 'running_test', _('running_test')
        TERMINATED = 'terminated', _('terminated')

    name = models.CharField(max_length=100, db_index=True)
    status = models.CharField(
        max_length=30,
        choices=StatusChoices.choices,
        default=StatusChoices.IDLE,
    )
    ip = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        ordering = ['status']


class Attack(TimeStampedModel):

    class StatusChoices(models.TextChoices):
        NEW = 'new', _('new')
        RUNNING = 'running', _('running')
        FINISHED = 'finished', _('finished')

    name = models.CharField(max_length=100)
    status = models.CharField(
        max_length=30,
        choices=StatusChoices.choices,
        default=StatusChoices.NEW,
    )
    instances = models.ManyToManyField(to=Instance, related_name='attacks_history')
    sh_command = models.TextField()
