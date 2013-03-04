from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from re import sub

class Category(models.Model):
	name = models.CharField(max_length=200, unique=True)
	created_on = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey(User, blank=True)
	def __unicode__(self):
		return u'%s' % self.name
	def slugname(self):
		return sub('[^A-Za-z0-9]+', '', self.name.lower())


class Tool(models.Model):
	name = models.CharField(max_length=200, unique=True)
	description = models.TextField()
	website = models.URLField()
	changelog_feed = models.URLField(blank=True)
	categories = models.ManyToManyField(Category, related_name="tools")
	user = models.ForeignKey(User)
	created_on = models.DateTimeField(auto_now_add=True)
	updated_on = models.DateTimeField(auto_now=True)
	
	def update_rating(self):
		try: ag_rating = AggregateRating.objects.get(tool_id = self.id)
		except: ag_rating = AggregateRating.objects.create(tool_id = self.id, value = 0)

		# for now, do a simple sum of all ratings. do something fancier and more interesting later
		calculated_rating = Rating.objects.filter(tool_id = self.id).aggregate(Sum('value'))
		ag_rating.value = calculated_rating['value__sum']
		ag_rating.save()
		return ag_rating.value

	def __unicode__(self):
		return u'%s' % self.name


class Toolbox(models.Model):
	name = models.CharField(max_length=200, unique=True)
	description = models.CharField(max_length=200, blank=True)
	user = models.ForeignKey(User, related_name='toolboxes')
	is_private = models.BooleanField(default=False)
	tools = models.ManyToManyField(Tool, related_name = "toolboxes")
	created_on = models.DateTimeField(auto_now_add=True)
	updated_on = models.DateTimeField(auto_now=True)
	def __unicode__(self):
		return u'%s' % self.name


class Rating(models.Model):
	user = models.ForeignKey(User)
	tool = models.ForeignKey(Tool, related_name='individual_ratings')
	value = models.IntegerField()
	created_on = models.DateTimeField(auto_now_add=True)
	def __unicode__(self):
		return u'%s - %s' % (self.user.username, self.tool.name)


class AggregateRating(models.Model):
	tool = models.OneToOneField(Tool, related_name = "rating")
	value = models.IntegerField()
	updated_on = models.DateTimeField(auto_now=True)
	def __unicode__(self):
		return u'%s - %s' % (self.tool.name, self.value)







