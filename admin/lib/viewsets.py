from rest_framework.viewsets import ModelViewSet as Rest_ModelViewSet


class ModelViewSet(Rest_ModelViewSet):
    """
    Extend DRF's ModelViewSet for update to act as partial_update.
    """

    def update(self, request, pk=None, **kwargs):
        """
        Update an element (acts as partial_update).
        """
        kwargs['partial'] = True
        return super().update(request, pk, **kwargs)
