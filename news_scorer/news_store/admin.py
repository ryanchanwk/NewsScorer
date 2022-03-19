from django.contrib import admin
from news_store.models import NewsSource, NewsStore, SentimentSource, SentimentStore, NewsSourceTag
import csv
from django.http import HttpResponse


class ExportCsvMixin:
    def export_as_csv(self, request, queryset):

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected row to CSV"


class NewsSourceAdmin(admin.ModelAdmin):
    list_display = ['source_name', 'source_url', 'is_active']



class NewsStoreAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ['title', 'news_source', 'actual_news_source', 'news_source_tag', 'news_datetime',
                    'create_datetime', 'news_url']
    list_filter = ['news_source', 'actual_news_source']
    ordering = ['-news_datetime']
    actions = ["export_as_csv"]
    date_hierarchy = 'news_datetime'


class SentimentStoreAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ['news_store', 'sentiment_source', 'predicted_class', 'create_datetime']
    ordering = ['-create_datetime']
    raw_id_fields = ['news_store']
    actions = ["export_as_csv"]
    date_hierarchy = 'create_datetime'


admin.site.register(NewsSource, NewsSourceAdmin)
admin.site.register(NewsStore, NewsStoreAdmin)
admin.site.register(SentimentSource)
admin.site.register(SentimentStore, SentimentStoreAdmin)
admin.site.register(NewsSourceTag)
