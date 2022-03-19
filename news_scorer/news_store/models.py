import logging

from django.db import models, IntegrityError

logger = logging.getLogger(__name__)


# Create your models here.
class NewsSource(models.Model):
    source_name = models.CharField(unique=True, max_length=256)
    source_url = models.URLField()
    parent_url = models.CharField(null=True, blank=True, max_length=512)
    is_integrate_source = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    source_timezone = models.CharField(default='US/Eastern', max_length=256)
    description = models.TextField(null=True, blank=True)
    create_datetime = models.DateTimeField(auto_now_add=True)
    excluded_source = models.ManyToManyField("NewsSource", blank=True)
    enable_tag = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.source_name}'


class NewsStore(models.Model):
    title = models.CharField(null=True, blank=True, max_length=256)
    body = models.TextField(null=True, blank=True)
    news_url = models.CharField(unique=True, max_length=512)
    news_source = models.ForeignKey('NewsSource', on_delete=models.PROTECT, related_name='parser_source')
    actual_news_source = models.ForeignKey('NewsSource', on_delete=models.PROTECT, related_name='actual_source',
                                           default=None, null=True)
    remark = models.TextField(null=True, blank=True)
    news_datetime = models.DateTimeField(null=True, blank=True)
    execution_batch = models.CharField(null=True, blank=True, max_length=256)
    create_datetime = models.DateTimeField(auto_now_add=True)
    news_source_tag = models.ForeignKey('NewsSourceTag', on_delete=models.PROTECT, default=None, null=True)

    def update_actual_news_store(self):
        if self.news_source.is_integrate_source is True:
            news_source = NewsSource.objects.all().values('id', 'parent_url')
            for item in list(news_source):
                if item['parent_url'] is not None:
                    if item['parent_url'].lower() in self.news_url:
                        self.actual_news_source = NewsSource.objects.get(pk=int(item['id']))
                        if self.actual_news_source in self.news_source.excluded_source.all():
                            logger.warning(
                                f'{self.news_source} {self.news_url} is removed because the source {self.actual_news_source} is in excluded list ')
                            self.delete()
                        else:
                            self.save()
                        return
            new_news_source = NewsSource.objects.create(source_name=self.news_url, source_url=self.news_url)
            self.actual_news_source = NewsSource.objects.get(pk=int(new_news_source.id))
            self.save()
        else:
            self.actual_news_source = self.news_source
            self.save()

    def __str__(self):
        return f'{self.news_source}-{self.title}'


class NewsSourceTag(models.Model):
    tag = models.CharField(null=True, blank=True, max_length=256)
    news_source = models.ForeignKey('NewsSource', on_delete=models.PROTECT)
    is_active = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['tag', 'news_source'], name='unique_tag_news_source')
        ]

    @staticmethod
    def get_or_create_news_source_tag(source, text):
        try:
            obj, _ = NewsSourceTag.objects.get_or_create(tag=text, news_source=source, is_active=True)
            logger.info(f'{obj} is added')
        except IntegrityError:
            obj = NewsSourceTag.objects.get(tag=text, news_source=source)
        return obj

    def __str__(self):
        return f'{self.news_source} {self.tag}'


class SentimentSource(models.Model):
    source_name = models.CharField(unique=True, max_length=256)
    token_model_name = models.CharField(default=None, null=True, max_length=256)
    pretrain_model_path = models.CharField(default=None, null=True, blank=True, max_length=512)
    pretrain_model_config_path = models.CharField(default=None, null=True, blank=True, max_length=512)
    config_path = models.CharField(default=None, null=True, max_length=512)
    weight_path = models.CharField(default=None, null=True, max_length=512)

    def __str__(self):
        return f'{self.source_name}'


class SentimentStore(models.Model):
    news_store = models.ForeignKey('NewsStore', on_delete=models.PROTECT)
    sentiment_source = models.ForeignKey('SentimentSource', on_delete=models.PROTECT)
    predicted_text = models.TextField(default=None, null=True, blank=True)
    predicted_class = models.IntegerField()
    other_result = models.CharField(default=None, null=True, max_length=256)

    remark = models.TextField(default=None, null=True, blank=True)
    create_datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.news_store}-{self.sentiment_source}-{self.predicted_class}'
