from rest_framework.mixins import CreateModelMixin
from rest_framework.renderers import JSONRenderer
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_xml.renderers import XMLRenderer

from comments.mixins import GetUserMixin, FileRenderViewMixin
from comments.models import CommentsReport, FINISHED
from comments.serializers.comments_report import CommentsReportSerializer


class CommentsReportsViewSet(GetUserMixin, CreateModelMixin, ReadOnlyModelViewSet):
    """
    This endpoint used to show and create commentaries reports.
    """
    serializer_class = CommentsReportSerializer
    queryset = CommentsReport.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.get_user())


class CommentsReportsResultViewSet(FileRenderViewMixin, ReadOnlyModelViewSet):
    """
    This endpoint used to render report file.
    """

    serializer_class = CommentsReportSerializer
    queryset = CommentsReport.objects.filter(status=FINISHED)

    export_format = 'format_name'
    filename = 'export'
    renderers_map = {
        'xml': XMLRenderer,
        'json': JSONRenderer,
    }
