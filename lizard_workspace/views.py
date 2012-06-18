# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
import datetime
import iso8601
import csv

from django.core.urlresolvers import reverse
from django.http import HttpResponse
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

    def csv_response(self):
        """
        Return common collage information and stats of collage items.
        """
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=collage.csv'

        collage = self.collage()
        date_range = current_start_end_dates(
            self.request, for_form=True)

        writer = csv.writer(response)
        writer.writerow(['naam', collage.name])
        writer.writerow(['periode', date_range['dt_start'], date_range['dt_end']])
        writer.writerow(['zomer of winter', LayerCollage.SUMMER_WINTER_DICT[collage.summer_or_winter]])
        writer.writerow(['dag of nacht', LayerCollage.DAY_NIGHT_DICT[collage.summer_or_winter]])
        writer.writerow(['maand', collage.display_month()])
        writer.writerow(['dag van de week', collage.display_day()])

        writer.writerow([
                'locatie', 'aantal waardes',
                'min', 'datum min',
                'max', 'datum max',
                'gem',
                'som',
                'grenswaarde', 'aantal <= grenswaarde', 'aantal > grenswaarde',
                'percentiel mediaan', 'percentiel 90',
                'percentiel gebruiker', 'percentiel instelling'])

        for stats in self.collage_stats():
            writer.writerow([
                    stats['name'], stats['item_count'],
                    stats['standard']['min'][1][0], stats['standard']['min'][0],
                    stats['standard']['max'][1][0], stats['standard']['max'][0],
                    stats['standard']['avg'],
                    stats['standard']['sum'],
                    stats['boundary']['value'],
                    stats['boundary']['amount_less_equal'],
                    stats['boundary']['amount_greater'],
                    stats['percentile']['median'],
                    stats['percentile']['90'],
                    stats['percentile']['user'],
                    stats['percentile']['value'],
                    ])

        return response

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

        response_format = request.GET.get('format', 'html')
        if response_format == 'csv':
            # Return csv format
            return self.csv_response()
        else:
            # Return normal page, 'html'
            return super(CollageView, self).get(request, *args, **kwargs)

    def graphs_by_grouping_hint(self):
        """Return a list of graph urls with metadata, grouped by grouping_hint"""

        # collect urls by grouping hint
        grouped_items = {}
        for collage_item in self.collage().layercollageitem_set.all():
            grouping_hint = collage_item.grouping_hint
            if grouping_hint not in grouped_items:
                grouped_items[grouping_hint] = []
            grouped_items[grouping_hint].append({
                    'name': collage_item.name,
                    'graph_params': collage_item.graph_url(only_parameters=True)
                    })

        # Now make items of it
        result = []
        base_url = reverse('lizard_graph_graph_view')
        for key, value in grouped_items.items():
            name = '%s: %s' % (key, ', '.join([v['name'] for v in value]))
            graph_url = '%s?%s' % (
                base_url, '&'.join([v['graph_params'] for v in value] + ['legend-location=7', ]))
            result.append({
                    'name': name,
                    'graph_url': graph_url})

        return result


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
