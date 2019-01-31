from datetime import datetime
from functools import reduce

import operator

import pytz

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.db import models

from mptt.models import MPTTModel, TreeForeignKey

from comments.mixins import ContentTypeMixin

CONTENT_TYPE_CHOICES = reduce(
    operator.or_,
    [models.Q(app_label=k, model=m) for k, v in
     getattr(settings, 'COMMENTED_CONTENT_TYPES', {}).items() for m in v]
)


class Comment(ContentTypeMixin, MPTTModel):
    """
    Comments model based on modified preorder traversal tree algorithm
    """
    parent = TreeForeignKey('self', on_delete=models.PROTECT, null=True, blank=True, related_name='children')
    text = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT, limit_choices_to=CONTENT_TYPE_CHOICES)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class MPTTMeta:
        order_insertion_by = ['created_at']

    class Meta:
        index_together = ('content_type', 'object_id')


CREATED = 'created'
UPDATED = 'updated'
DELETED = 'deleted'
LOG_OPERATIONS = (
    (CREATED, 'created'),
    (UPDATED, 'updated'),
    (DELETED, 'deleted'),
)


class CommentActivityLog(models.Model):
    """
    Keeps state before and after comment changes
    """
    comment_id = models.PositiveIntegerField(db_index=True)
    operation = models.CharField(max_length=20, choices=LOG_OPERATIONS, default=CREATED)
    state_before = JSONField(null=True, default=None)
    state_after = JSONField(null=True, default=None)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


PENDING = 'pending'
FINISHED = 'finished'
FAILED = 'failed'
STATUSES = (
    (PENDING, 'pending'),
    (FINISHED, 'finished'),
    (FAILED, 'failed'),
)


class CommentsReport(models.Model):
    """
    Generated reports fo comments
    """
    status = models.CharField(max_length=20, choices=STATUSES, default=PENDING)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    report_params = JSONField(default=dict)
    report_data = JSONField(null=True)

    @staticmethod
    def get_param_value(value):
        if isinstance(value, models.Model):
            return value.id
        if isinstance(value, datetime):
            return value.timestamp()
        return value

    @staticmethod
    def timestamp2datetime(value):
        return datetime.utcfromtimestamp(value).replace(tzinfo=pytz.utc) if value else value

    def format_report_params(self, ignore_empty=True):
        params = dict()
        report_params = ('user_id', 'content_type_id', 'object_id', 'created_at__gte', 'created_at__lt')
        for key in report_params:
            value = getattr(self, key, None)
            if value and ignore_empty:
                params[key] = value
            elif not ignore_empty:
                params[key] = value
        return params

    @property
    def user_id(self):
        return self.report_params.get('user_id')

    @user_id.setter
    def user_id(self, value):
        self.report_params['user_id'] = self.get_param_value(value)

    @property
    def content_type_id(self):
        return self.report_params.get('content_type_id')

    @content_type_id.setter
    def content_type_id(self, value):
        self.report_params['content_type_id'] = self.get_param_value(value)

    @property
    def object_id(self):
        return self.report_params.get('object_id')

    @object_id.setter
    def object_id(self, value):
        self.report_params['object_id'] = value

    @property
    def created_at__gte(self):
        return self.timestamp2datetime(self.report_params.get('created_at__gte'))

    @created_at__gte.setter
    def created_at__gte(self, value):
        self.report_params['created_at__gte'] = self.get_param_value(value)

    @property
    def created_at__lt(self):
        return self.timestamp2datetime(self.report_params.get('created_at__lt'))

    @created_at__lt.setter
    def created_at__lt(self, value):
        self.report_params['created_at__lt'] = self.get_param_value(value)


class Subscribe(models.Model):
    """
    Subscription to  commentaries of entity
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT, limit_choices_to=CONTENT_TYPE_CHOICES)
    object_id = models.PositiveIntegerField()

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')
        index_together = ('content_type', 'object_id')
