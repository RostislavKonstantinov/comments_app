from django.contrib.contenttypes.models import ContentType
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND

from comments.utils import get_user_from_request


class ContentTypeMixin:
    """
    Add methods for get content type of current models.Model class
    """

    @property
    def self_content_type(self):
        return self.get_content_type().id

    @classmethod
    def get_content_type(cls):
        return ContentType.objects.get_for_model(cls)


class GetUserMixin:
    """
    Get user object from request field "user"
    Only for test app use
    """

    def get_user(self, raise_errors=True):
        return get_user_from_request(self.request, raise_errors)


class NotEditableFieldsMixin:
    """
    Adds support for not editable fields to serializers.

    To use it, specify a list of fields as `not_editable_fields` on the
    serializer's Meta:
    ```
    class Meta:
        model = SomeModel
        fields = '__all__'
        not_editable_fields = ('collection', )
    ```
    """

    def get_fields(self):
        fields = super().get_fields()
        not_editable_fields = getattr(self.Meta, 'not_editable_fields', None)
        if not self.instance or not not_editable_fields:
            return fields

        if not isinstance(not_editable_fields, (list, tuple)):
            raise TypeError(
                'The `not_editable_fields` option must be a list or tuple. '
                'Got {}.'.format(type(not_editable_fields).__name__)
            )

        for field_name in not_editable_fields:
            if field_name in fields:
                fields[field_name].read_only = True

        return fields


class FileRenderViewMixin:
    export_format = None
    """
    Add support for render files from json and load it to views

    To use it, specify a name of file and format-renderers map
    Renderer should be child of BaseRenderer
    ```
    class CustomView(FileRenderViewMixin, GenericViewSet):
        ....
        export_format = 'format_name'
        filename = 'export'
        renderers_map = {
            'xml': XMLRenderer,
            'json': JSONRenderer,
        }
    ```
    """

    def get_renderer(self):
        return self.renderers_map.get(self.get_format())

    def get_renderers(self):
        renderer = self.get_renderer()
        if renderer:
            return [renderer()]
        return super().get_renderers()

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(
            request, response, *args, **kwargs
        )
        response["content-disposition"] = f'attachment; filename={self.get_filename()}.{self.get_format()}'
        return response

    def get_filename(self):
        return self.filename

    def get_format(self):
        return self.kwargs.get(self.export_format)

    def retrieve(self, request, *args, **kwargs):
        if not self.get_renderer():
            return Response(status=HTTP_404_NOT_FOUND)
        instance = self.get_object()
        return Response(instance.report_data)
