from django import template
from django.contrib.auth.models import Group
from core.models import Message, Ticket

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    try:
        group = Group.objects.get(name=group_name)
        return group in user.groups.all()
    except Group.DoesNotExist:
        return False

@register.filter(name='is_support')
def is_support(user):
    try:
        group = Group.objects.get(name='Support')
        return group in user.groups.all()
    except Group.DoesNotExist:
        return False

@register.filter(name='is_auditor')
def is_support(user):
    try:
        group = Group.objects.get(name='Auditor')
        return group in user.groups.all()
    except Group.DoesNotExist:
        return False

@register.simple_tag(takes_context=True)
def is_ticket_owner(context, ticket_id):
    request = context['request']
    user = request.user

    try:
        ticket = Ticket.objects.get(pk=ticket_id)
    except Ticket.DoesNotExist:
        return False

    first_message = Message.objects.filter(ticket=ticket).order_by('created_on').first()
    return first_message is not None and first_message.user == user

@register.filter
def is_owner_of_message(user, message):
    if not user or not message:
        return False
    return message.user == user