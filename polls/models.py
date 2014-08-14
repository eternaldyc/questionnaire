from django.db import models
from django.utils import timezone
import datetime
# Create your models here.
class Poll(models.Model):
    question = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    
    def __unicode__(self):  # Python 3: def __str__(self):
        return self.question
        
    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

class Choice(models.Model):
    poll = models.ForeignKey(Poll)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    
    def __unicode__(self):  # Python 3: def __str__(self):
        return self.choice_text
        
class Userdata(models.Model):
    user_id = models.IntegerField()
    info_type = models.IntegerField()
    info_content = models.CharField(max_length=100)
    info_datetime = models.DateTimeField('input time')
    
    def __unicode__(self):  # Python 3: def __str__(self):
        return self.user_id + info_type + info_content