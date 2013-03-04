from django.conf.urls.defaults import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

import datetime
from feedparser import parse
from random import choice

from awesometoolbox.models import *
from awesometoolbox.forms import *


def index(request):
    newest_tools = Tool.objects.order_by('-created_on')
    return render_to_response(
        'tool_listing.html', 
        {
            'page_title':'Newest Tools',
            'tools': newest_tools
        },
        context_instance=RequestContext(request)
    )



def all_tools(request):
    all_tools = Tool.objects.order_by('name')
    return render_to_response(
        'tool_listing.html', 
        {
            'page_title':'All Tools',
            'tools': all_tools
        },
        context_instance=RequestContext(request)
    )



@login_required
def new_tool(request):
    if request.method == 'POST':
        form = ToolForm(request.POST)
        form.instance.user_id = request.user.id
        form.categories = request.POST['categories']

        if form.is_valid():
            tool = form.save()
            for category in form.categories.replace(", ", ",").split(","):
                tool.categories.add(Category.objects.get_or_create(name = category,defaults = { 'user_id' : 1 })[0])

            messages.add_message(request, messages.SUCCESS, '%s was successfully created!' % tool.name)
            return redirect('index')
        else:
            messages.add_message(request, messages.ERROR, 'There seems to be a problem. Review your litany of transgressions below.')

    else: form = ToolForm()

    return render_to_response(
        'tool_form.html', 
        { 'page_title': 'New Tool', 'form': form, },
        context_instance=RequestContext(request)
    )   



def delete_tool(request, tool_id):
    tool = Tool.objects.get(id = tool_id)
    if tool.user == request.user:

        # clean up categories that are about to not have any tools in them
        for category in tool.categories.all():
            if category.tools.all().exclude(name=tool.name).count() == 0:
                category.delete()

        tool.delete()

        messages.add_message(request, messages.SUCCESS, '%s was successfully created!' % tool.name)
        return redirect('index')

    else:
        messages.add_message(request, messages.ERROR, '%s ain\'t your tool, buddy.' % tool.name)
        return redirect('tool_page', tool_id)


def tool_page(request, tool_id):
    tool = Tool.objects.get(id = tool_id)
    related_category = choice(tool.categories.all())
    related_tools = Tool.objects.filter(categories = related_category).exclude(id=tool.id)

    if tool.changelog_feed:
        changelog = parse(tool.changelog_feed)
        changelog_title = changelog['feed']['title']
        changelog_entries = []
        for entry in changelog['entries'][:5]:
            changelog_entries.append({
                'title':    entry['title'],
                'author':   entry['author'],
                'date':     datetime.datetime.strptime(sub('-\d\d:\d\d$', '', entry['updated']), "%Y-%m-%dT%H:%M:%S"),
                'link':     entry['link'],
                })
    else:
        changelog_title = False
        changelog_entries = False

    return render_to_response(
        'tool_page.html', 
        {
            'page_title': tool.name,
            'tool': tool,
            'related_category':related_category,
            'related_tools':related_tools,
            'changelog_title':changelog_title,
            'changelog_entries':changelog_entries
        },
        context_instance=RequestContext(request)
    )



def toolbox_page(request, toolbox_id):
    toolbox = Toolbox.objects.get(id = toolbox_id)

    return render_to_response(
        'tool_listing.html', 
        {
            'page_title': toolbox.name,
            'page_subtitle': toolbox.description,
            'tools': toolbox.tools.order_by('name'),
            'toolbox': toolbox,
        },
        context_instance=RequestContext(request)
    )


@login_required
def new_toolbox(request):
    if request.method == 'POST':
        form = ToolboxForm(request.POST)
        form.instance.user_id = request.user.id

        if form.is_valid():
            toolbox = form.save()
            messages.add_message(request, messages.SUCCESS, '%s was successfully created. Start adding some tools!' % toolbox.name)
            return redirect('index')
        else:
            messages.add_message(request, messages.ERROR, 'There seems to be a problem. Review your litany of transgressions below.')

    else: form = ToolboxForm()

    return render_to_response(
        'toolbox_form.html', 
        { 'page_title': 'New Toolbox', 'form': form, },
        context_instance=RequestContext(request)
    )   



def delete_toolbox(request, toolbox_id):
    toolbox = Toolbox.objects.get(id = toolbox_id)
    toolboxname = toolbox.name
    if request.user == toolbox.user:
        toolbox.delete()
        messages.add_message(request, messages.SUCCESS, '%s was successfully deleted.' % toolboxname)
        return redirect('index')
    else:
        messages.add_message(request, messages.ERROR, '%s ain\'t your toolbox, buddy.' % toolboxname)
        return redirect('index')



def add_tool_to_toolbox(request, toolbox_id, tool_id):
    toolbox = Toolbox.objects.get(id = toolbox_id)
    tool = Tool.objects.get(id = tool_id)
    if request.user == toolbox.user:
        if tool not in toolbox.tools.all():
            toolbox.tools.add(tool)
            messages.add_message(request, messages.SUCCESS, '%s was successfully added to %s.' % (tool.name, toolbox.name))
            return redirect('toolbox_page', toolbox_id)
        else:
            messages.add_message(request, messages.WARNING, '%s is already in %s.' % (tool.name, toolbox.name))
            return redirect('toolbox_page', toolbox_id)
    else:
        messages.add_message(request, messages.ERROR, '%s ain\'t your toolbox, buddy.' % toolbox.name)
        return redirect('toolbox_page', toolbox_id)



def remove_tool_from_toolbox(request, toolbox_id, tool_id):
    toolbox = Toolbox.objects.get(id = toolbox_id)
    tool = Tool.objects.get(id = tool_id)
    if request.user == toolbox.user:
        if tool in toolbox.tools.all():
            toolbox.tools.remove(tool)
            messages.add_message(request, messages.SUCCESS, '%s was successfully removed from %s.' % (tool.name, toolbox.name))
            return redirect('toolbox_page', toolbox_id)
        else:
            messages.add_message(request, messages.WARNING, '%s isn\'t in %s.' % (tool.name, toolbox.name))
            return redirect('toolbox_page', toolbox_id)
    else:
        messages.add_message(request, messages.ERROR, '%s ain\'t your toolbox, buddy.' % toolbox.name)
        return redirect('toolbox_page', toolbox_id)



def category_page(request, category_id):
    category = Category.objects.get(id = category_id)
    category_tools = Tool.objects.filter(categories = category)
    category_tab = category.id
    return render_to_response(
        'tool_listing.html', 
        {
            'page_title': category.name,
            'tools': category_tools,
            'category_tab': category_tab,
        },
        context_instance=RequestContext(request)
    )



def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.add_message(request, messages.SUCCESS, 'Welcome back, %s' % user.username)
                return redirect('index')
            else:
                messages.add_message(request, messages.ERROR, 'Your account is disabled.')
                return redirect('index')
        else:
            messages.add_message(request, messages.ERROR, 'Username or password incorrect.')

    return render_to_response(
        'login.html', { 'page_title': 'Welcome back.'},
        context_instance=RequestContext(request)
    )



def logout_view(request):
    name = str(request.user.username)
    logout(request)
    messages.add_message(request, messages.SUCCESS, 'See ya later, %s' % name)
    return redirect('index')


def signup(request):
    if request.user.is_authenticated():
        messages.add_message(request, messages.ERROR, 'You\'re already logged in as %s!.' % request.user.username)
        return redirect('index')

    manipulator = RegistrationForm()
    if request.POST:
        new_data = request.POST.copy()
        errors = manipulator.get_validation_errors(new_data)
        if not errors:
            # Save the user                                                                                                                                                 
            manipulator.do_html2python(new_data)
            new_user = manipulator.save(new_data)
            login(new_user)            
            messages.add_message(request, messages.SUCCESS, 'Thanks for signing up, %s!.' % new_user.username)
            return redirect('index')

    else:
        errors = new_data = {}
    form = forms.FormWrapper(manipulator, new_data, errors)
    return render_to_response('signup.html', {'page_title':'Register','form': form})





@login_required
def add_rating(request, tool_id, rating_value):

    tool = Tool.objects.get(id=tool_id)
    # parse rating_value
    if rating_value == "1":
        calculated_rating = 1
    elif rating_value == "0":
        calculated_rating = 0
    else:
        messages.add_message(request, messages.ERROR, 'Dafuq?')
        return redirect('tool_page', tool_id)

    try:
        rating = Rating.objects.get(tool_id = tool_id, user_id = request.user.id)
        if rating.value == calculated_rating:
            # if the user has previously rated this tool with this value, do nothing
            messages.add_message(request, messages.WARNING, 'You\'ve already rated this tool!')

        else:
            # if the user has previously rated this tool, but the rating is different, change it
            rating.value = calculated_rating
            rating.save()
            messages.add_message(request, messages.SUCCESS, 'Your rating has been changed!')

    except:
        rating = Rating(tool_id = tool_id, user_id = request.user.id, value = calculated_rating).save()
        messages.add_message(request, messages.SUCCESS, 'Thanks for submitting your rating!')

    tool.update_rating()
    return redirect('tool_page', tool_id)
