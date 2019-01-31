import logging

from django.db import connection

from comments.models import CommentsReport, Comment, PENDING, FAILED, FINISHED
from comments.serializers.comment import CommentSerializer
from comments.sql import REPORT_SQL
from events import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name='debug')
def comments_debug_task():
    logger.info('It is working!')


@celery_app.task(name='comments_report')
def generate_comments_report(report_id):
    """
    Generate comment report
    :param report_id: id of comment report
    :return:
    """
    try:
        report = CommentsReport.objects.get(id=report_id)
    except CommentsReport.DoesNotExist:
        logging.error(f"Comments report with id={report_id} does not exists")
        return

    if report.status != PENDING:
        logger.info(f"Comments report id={report_id} have't got pending status")
        return

    serializer = CommentSerializer
    params = report.format_report_params()

    try:
        if not params:
            raise ValueError(f"Comments report id={report_id} parameters are empty")

        if 'content_type_id' in params:
            report.report_data = []
            with connection.cursor() as cursor:
                # SQL optimization
                cursor.execute(REPORT_SQL, report.format_report_params(False))
                for row, in cursor:
                    report.report_data.append(row)
        else:
            report.report_data = serializer(
                Comment.objects.filter(**params).select_related('user'),
                many=True
            ).data
        report.status = FINISHED
    except Exception:
        report.status = FAILED
        logging.exception(f"Comments report id={report_id} failed")
    finally:
        report.save()
    logger.info(f"Comments report id={report_id} finished")
