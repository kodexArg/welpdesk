from django.shortcuts import render, get_object_or_404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.db import models

from .models import UDN, Sector, IssueCategory, Issue, Ticket

@login_required(login_url='login')
def htmx_udn(request):
    if request.user.is_staff:
        udns = UDN.objects.all()
    else:
        user_groups = request.user.groups.all()
        udns = UDN.objects.filter(
            models.Q(permission_group__in=user_groups) | 
            models.Q(groups__in=user_groups)
        ).distinct()
    return render(request, 'ticket/partials/create/udn.html', {'udns': udns})

@login_required(login_url='login')
def htmx_sector(request, udn):
    udn_obj = get_object_or_404(UDN, id=udn)
    if request.user.is_staff:
        sectors = Sector.objects.filter(udn=udn_obj)
    else:
        user_groups = request.user.groups.all()
        sectors = Sector.objects.filter(
            udn=udn_obj
        ).filter(
            models.Q(permission_group__in=user_groups) | 
            models.Q(groups__in=user_groups)
        ).distinct()
    return render(request, 'ticket/partials/create/sector.html', {'sectors': sectors})

@login_required(login_url='login')
def htmx_issue_category(request, sector):
    issue_categories = IssueCategory.objects.filter(sector__id=sector)
    return render(request, 'ticket/partials/create/issue-category.html', {'issue_categories': issue_categories})

@login_required(login_url='login')
def htmx_issue(request, issue_category):
    issues = Issue.objects.filter(issue_category=issue_category)
    return render(request, 'ticket/partials/create/issue.html', {'issues': issues})

@login_required(login_url='login')
def htmx_ticket_details(request, issue):
    issue_obj = get_object_or_404(Issue, id=issue)
    return render(request, 'ticket/partials/create/ticket-details.html', {
        'issue': issue_obj
    })

@login_required(login_url='login')
def htmx_add_attachment(request):
    max_index = -1
    if request.method == 'POST':
        if 'attachment-highest-index' in request.POST:
            try:
                max_index = int(request.POST.get('attachment-highest-index', '-1'))
            except ValueError:
                pass
        for key in request.POST:
            if key.startswith('attachment-file-') or key.startswith('attachment-name-'):
                try:
                    index = int(key.split('-')[-1])
                    max_index = max(max_index, index)
                except ValueError:
                    pass
        for key in request.FILES:
            if key.startswith('attachment-file-'):
                try:
                    index = int(key.split('-')[-1])
                    max_index = max(max_index, index)
                except ValueError:
                    pass
    new_index = max_index + 1
    return render(request, 'ticket/partials/attachment-item.html', {
        'index': new_index
    })

@login_required(login_url='login')
def htmx_remove_attachment(request):
    return HttpResponse('')

@login_required(login_url='login')
def htmx_confirm_close_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    return render(request, 'ticket/partials/modal-confirm.html', {'ticket': ticket})
