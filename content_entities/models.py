from django.db import models

from comments.mixins import ContentTypeMixin


class AbstractContentEntity(ContentTypeMixin, models.Model):
    """
    Only for test app
    """
    title = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def content_type(self):
        return self.get_content_type().id

    class Meta:
        abstract = True
        ordering = ['-created_at']


class Blog(AbstractContentEntity):
    pass


class Topic(AbstractContentEntity):
    pass
