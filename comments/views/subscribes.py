from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from comments.filters import SubscribesFilter
from comments.mixins import GetUserMixin
from comments.models import Subscribe
from comments.serializers.subscribe import SubscribeSerializer


class SubscribesViewSet(GetUserMixin,
                        mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.DestroyModelMixin,
                        mixins.ListModelMixin,
                        GenericViewSet):
    """
    This endpoint used to show, add and delete subscribes.
    """
    serializer_class = SubscribeSerializer
    queryset = Subscribe.objects.all()
    filter_class = SubscribesFilter

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data.update(user=self.get_user().id)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
