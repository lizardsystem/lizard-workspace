# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

from lizard_map.views import DateRangeMixin
from lizard_ui.views import UiView

from lizard_workspace.models import LayerCollage


class CollageView(DateRangeMixin, UiView):
    template_name = 'lizard_workspace/collage.html'

    def collage(self):
        """Return collage"""
        if not hasattr(self, '_collage'):
            if self.collage_id:
                self._collage = LayerCollage.objects.get(
                    pk=self.collage_id)
            else:
                self._collage = None
        return self._collage

    def collage_info(self):
        """Info for all collage items"""
        return self.collage().info()

    def collage_stats(self):
        """Info of individual collage items"""
        result = []
        for collage_item in self.collage().layercollageitem_set.all():
            stats = collage_item.info_stats()
            result.append(stats)
        return result

    def get(self, request, *args, **kwargs):
        self.collage_id = kwargs.get('collage_id', None)
        return super(CollageView, self).get(request, *args, **kwargs)
