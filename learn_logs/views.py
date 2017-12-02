from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from .models import Topic, Entry
from .forms import TopicForm, EntryForm
from django.contrib.auth.decorators import login_required
# Create your views here.


def index(request):
    """学习笔记的主页"""
    return render(request, 'learn_logs/index.html')


@login_required()
def topics(request):
    """显示主题"""
    topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    context = {'topics': topics}
    return render(request, 'learn_logs/topics.html', context)


@login_required()
def topic(request, topic_id):
    """显示单个主题及其所有条目"""
    topic = Topic.objects.get(id=topic_id)
    if topic.owner != request.user:
        raise Http404
    entries = topic.entry_set.order_by('-date_added')
    context = {'topic': topic, 'entries': entries}
    return render(request, 'learn_logs/topic.html', context)


@login_required()
def new_topic(request):
    """添加新主题"""
    if request.method != 'POST':
        form = TopicForm()
    else:
        form = TopicForm(request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return HttpResponseRedirect(reverse('learn_logs:topics'))

    context = {'form': form}
    return render(request, 'learn_logs/new_topic.html', context)


@login_required()
def new_entry(request, topic_id):
    """特定的主题中添加新条目"""
    topic = Topic.objects.get(id=topic_id)

    if request.method != 'POST':
        # 未提交数据，创建一个空表单
        form = EntryForm()
    else:
        # Post 提交的数据，对数据进行处理
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return HttpResponseRedirect(reverse('learn_logs:topic',
                                                args=[topic_id]))

    context = {'topic': topic, 'form': form}
    return render(request, 'learn_logs/new_entry.html', context)


@login_required()
def edit_entry(request, entry_id):
    """编辑既有条目"""
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    if topic.owner != request.user:
        raise Http404

    if request.method != 'POST':
        # 初次请求，使用当前条目填充表单
        form = EntryForm(instance=entry)
    else:
        # POST提交的数据，对数据进行处理
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('learn_logs:topic',
                                                args=[topic.id]))
    context = {'entry': entry, 'topic': topic, 'form': form}
    return render(request, 'learn_logs/edit_entry.html', context)


@login_required()
def del_topic(request, topic_id):
    """删除主题，如果主题下有内容，也会删除主题"""
    errors = ""
    topic = Topic.objects.get(id=topic_id)
    # 如果主题存在，判断主题下是否有内容
    if topic:
        topics = Topic.objects.filter(owner=request.user).order_by('date_added')
        context = {'topics': topics}
        Topic.objects.filter(id=topic_id).delete()
        return render(request, 'learn_logs/topics.html', context)
    else:
        errors = "参数异常请刷新后重试"
        context = {'errors': errors}
        return render(request, 'learn_logs/topics.html', context)