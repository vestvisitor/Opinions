from crispy_forms.layout import Submit
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Model
from django.utils import timezone


class CaseTag(models.Model):
    tag_title = models.CharField(max_length=50)

    def __str__(self):
        return self.tag_title


class Case(models.Model):
    case_title = models.CharField(max_length=100)
    tags = models.ManyToManyField(CaseTag)
    case_text = models.CharField(max_length=1000)
    pub_date = models.DateTimeField(timezone.now())
    is_anonymous = models.BooleanField(default=False)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.case_title[:20]


class Opinion(models.Model):
    opinion_text = models.CharField(max_length=1000)
    pub_date = models.DateTimeField("date published")
    is_anonymous = models.BooleanField(default=False)
    case = models.ForeignKey(Case, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.opinion_text[:20]
