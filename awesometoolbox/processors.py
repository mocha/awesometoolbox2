from django.conf import settings
from awesometoolbox.models import Category


def general(request):
	all_categories = Category.objects.order_by('name')
	return {
		'all_categories' : all_categories,
	}