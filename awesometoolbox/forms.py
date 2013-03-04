from django.core import validators
from django.forms import ModelForm
from django import forms

from awesometoolbox.models import Toolbox, Tool



class ToolboxForm(ModelForm):
	class Meta:
		model = Toolbox
		fields = ('name', 'description', 'is_private')



class ToolForm(ModelForm):
	class Meta:
		model = Tool
		fields = ('name', 'description', 'website', 'changelog_feed')
