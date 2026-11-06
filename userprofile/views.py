from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .forms import User_Profile
from userincome.models import Source


@login_required(login_url='/authentication/login')
def userprofile(request):
    sources = Source.objects.filter(owner=request.user)
    if request.method == "POST":
        form = User_Profile(data=request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile Updated Successfully!!')
    else:
        form = User_Profile(instance=request.user)
    return render(request, 'userprofile/profile.html', {'form': form, 'sources': sources})


@login_required(login_url='/authentication/login')
@require_POST
def addSource(request):
    new_source = request.POST.get('Source', '').strip()
    if not new_source:
        messages.error(request, 'Income source cannot be empty.')
    elif len(new_source) > 266:
        messages.error(request, 'Income source is too long.')
    elif Source.objects.filter(name=new_source, owner=request.user).exists():
        messages.warning(request, 'Income source already exists.')
    else:
        Source.objects.create(name=new_source, owner=request.user)
        messages.success(request, 'Source added successfully.')
    return redirect('account')


@login_required(login_url='/authentication/login')
@require_POST
def deleteSource(request, id):
    source = get_object_or_404(Source, pk=id, owner=request.user)
    source.delete()
    messages.success(request, 'Source deleted successfully.')
    return redirect('account')
