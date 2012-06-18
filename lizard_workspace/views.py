# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
import datetime
import iso8601

from django.http import HttpResponseRedirect

from lizard_map.daterange import compute_and_store_start_end
from lizard_map.daterange import current_start_end_dates
from lizard_map.views import DateRangeMixin
from lizard_ui.views import ViewContextMixin
from django.views.generic.base import TemplateView

from lizard_workspace.models import LayerCollage
from lizard_workspace.models import LayerCollageItem


class CollageView(DateRangeMixin, ViewContextMixin, TemplateView):
    template_name = 'lizard_workspace/collage.html'

    def date_range_url_params(self):
        date_range = current_start_end_dates(
            self.request, for_form=True)
        return '&dt_start=%(dt_start)s&dt_end=%(dt_end)s' % date_range

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
        start = self.date_start_period()
        end = self.date_end_period()
        for collage_item in self.collage().layercollageitem_set.all():
            stats = collage_item.info_stats(start=start, end=end)
            stats['id'] = collage_item.id
            result.append(stats)
        return result

    def get(self, request, *args, **kwargs):
        """
        Display collage.

        You can provide dt_start and dt_end to set system period.

        ?dt_start=2001-06-15%2015:06:32.118341&dt_end=2012-06-14%2015:06:32.118341
        """
        self.collage_id = kwargs.get('collage_id', None)
        # date_range: see lizard_map.daterange
        # 5 = last year
        # 6 = custom
        if 'dt_start' in request.GET and 'dt_end' in request.GET:
            dt_start = iso8601.parse_date(request.GET['dt_start'])
            # Get rid of time and tz info
            dt_start = datetime.datetime(dt_start.year, dt_start.month, dt_start.day)
            dt_end = iso8601.parse_date(request.GET['dt_end'])
            dt_end = datetime.datetime(dt_end.year, dt_end.month, dt_end.day)
            date_range = {'dt_end': dt_end, 'period': u'6', 'dt_start': dt_start}
            compute_and_store_start_end(request.session, date_range)
            return HttpResponseRedirect('./')
        return super(CollageView, self).get(request, *args, **kwargs)


class CollageItemView(ViewContextMixin, TemplateView):
    template_name = 'lizard_workspace/box_collage_item.html'

    def collage_item(self):
        if not hasattr(self, '_collage_item'):
            if self.collage_item_id:
                self._collage_item = LayerCollageItem.objects.get(
                    pk=self.collage_item_id)
            else:
                self._collage_item = None
        return self._collage_item

    def get(self, request, *args, **kwargs):
        self.collage_item_id = kwargs.get('collage_item_id', None)
        return super(CollageItemView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.collage_item_id = kwargs.get('collage_item_id', None)
        collage_item = self.collage_item()
        collage_item.boundary_value = float(request.POST['boundary_value'])
        collage_item.percentile_value = float(request.POST['percentile_value'])
        collage_item.save()
        return HttpResponseRedirect('./')


class CollageBoxView(ViewContextMixin, TemplateView):
    """
    Edit collage period settings:

    - summer/winter
    - day of week
    - day or night
    - restrict to month
    """
    template_name = 'lizard_workspace/box_collage.html'

    def collage(self):
        """Return collage"""
        if not hasattr(self, '_collage'):
            if self.collage_id:
                self._collage = LayerCollage.objects.get(
                    pk=self.collage_id)
            else:
                self._collage = None
        return self._collage

    def get(self, request, *args, **kwargs):
        self.collage_id = kwargs.get('collage_id', None)
        return super(CollageBoxView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.collage_id = kwargs.get('collage_id', None)
        collage = self.collage()
        collage.summer_or_winter = int(request.POST['summer_or_winter'])
        try:
            day_of_week = int(request.POST.get('day_of_week'))
        except ValueError:
            day_of_week = None
        collage.day_of_week = day_of_week
        try:
            restrict_to_month = int(request.POST.get('restrict_to_month'))
        except ValueError:
            restrict_to_month = None
        collage.restrict_to_month = restrict_to_month
        collage.day_or_night = int(request.POST['day_or_night'])
        collage.save()
        return HttpResponseRedirect('./')
