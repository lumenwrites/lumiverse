import datetime, re
from django.utils.timezone import utc

# Core django components
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# My own stuff
# Forms
from videos.forms import VideoForm
from comments.forms import CommentForm
# Models
from videos.models import Video
from .models import Comment


def comment_submit(request, video_slug):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            video = Video.objects.get(slug=video_slug)
            comment.video = video
            comment.save()

            comment_url = request.GET.get('next', '/')# +"#id-"+str(comment.id)
            return HttpResponseRedirect(comment_url)
        else:
            comment_url = request.GET.get('next', '/')
            return HttpResponseRedirect(comment_url)
    else:
            comment_url = request.GET.get('next', '/')
            return HttpResponseRedirect(comment_url)

def reply_submit(request, comment_id):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.parent = Comment.objects.get(id=comment_id)
            comment.video = comment.parent.video
            comment.save()


            comment_url = request.GET.get('next', '/')+"#id-"+str(comment.id)
            return HttpResponseRedirect(comment_url)
        else:
            comment_url = request.GET.get('next', '/')
            return HttpResponseRedirect(comment_url)            
        
        

def comment_edit(request, comment_id):
    comment = Comment.objects.get(id = comment_id)
    nextpage = request.GET.get('next', '/')

    if request.method == 'POST':
        form = CommentForm(request.POST,instance=comment)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.save()
            return HttpResponseRedirect(nextpage)
    else:
        form = CommentForm(instance=comment)
    
    return render(request, 'comments/comment-edit.html', {
        'comment':comment,
        'form':form,
        'nextpage':nextpage
    })
    
    # throw him out if he's not an author
    if request.user != comment.author:
        return HttpResponseRedirect('/')        
    return HttpResponseRedirect('/') # to video list

        
def comment_delete(request, comment_id):
    comment = Comment.objects.get(id = comment_id)

    # throw him out if he's not an author
    if request.user != comment.author:
        return HttpResponseRedirect('/')        
    try:
        path = '/video/'+comment.parent.video.slug # + '/' + comment.video.slug + '#comments'
    except:
        path = '/video/'+comment.video.slug + '#comments'

    comment.delete()

    return HttpResponseRedirect(path) # to video list

        
# Comment voting
# Voting
def comment_upvote(request):
    comment = Comment.objects.get(id=request.POST.get('comment-id'))
    comment.score += 1
    comment.save()
    comment.author.karma += 1
    comment.author.save()
    user = request.user
    user.comments_upvoted.add(comment)
    user.save()
    return HttpResponse()

def comment_downvote(request):
    comment = Comment.objects.get(id=request.POST.get('comment-id'))
    if comment.score > 0:
        comment.score -= 1
        comment.author.karma -= 1        
    comment.save()
    comment.author.save()
    user = request.user
    user.comments_downvoted.add(comment)
    user.save()
    return HttpResponse()

def comment_unupvote(request):
    comment = Comment.objects.get(id=request.POST.get('comment-id'))
    comment.score -= 1
    comment.save()
    comment.author.karma = 1
    comment.author.save()
    user = request.user
    user.comments_upvoted.remove(comment)
    user.save()
    return HttpResponse()

def comment_undownvote(request):
    comment = Comment.objects.get(id=request.POST.get('comment-id'))
    comment.score += 1
    comment.author.karma += 1        
    comment.save()
    comment.author.save()
    user = request.user
    user.comments_downvoted.remove(comment)
    user.save()
    return HttpResponse()
