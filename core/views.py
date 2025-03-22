from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import FormView, TemplateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.paginator import Paginator

from .forms import TicketCreationForm
from .models import IssueCategory, Issue, Message, Sector, Ticket, UDN, Attachment
from .logger import logger


class HomeView(TemplateView):
    template_name = 'base/home.html'

class DevelopmentView(TemplateView):
    template_name = 'base/development.html'



class TicketListView(LoginRequiredMixin, TemplateView):
    template_name = 'ticket/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        queryset = Ticket.objects.all() if self.request.user.is_staff else Ticket.objects.get_queryset(user=self.request.user).distinct()

        tickets = queryset.annotate(last_message_timestamp=models.Max('messages__created_on')).order_by('-last_message_timestamp')

        page_number = self.request.GET.get('page')
        paginator = Paginator(tickets, 6)
        page_obj = paginator.get_page(page_number)

        context['page_obj'] = page_obj
        context['tickets'] = page_obj.object_list

        return context


class CreateTicketView(LoginRequiredMixin, FormView):
    """
    Importante:
    - Al crear un nuevo ticket, se crea un mensaje (el primero) con el estado 'open'.
    """

    template_name = 'ticket/create.html'
    form_class = TicketCreationForm

    def form_valid(self, form):
        ticket = Ticket.objects.create(
            udn=form.cleaned_data['udn'],
            sector=form.cleaned_data['sector'],
            issue_category=form.cleaned_data['issue_category'],
            issue=form.cleaned_data['issue']
        )
        
        message = Message.objects.create(
            ticket=ticket,
            status='open',
            user=self.request.user,
            body=form.cleaned_data['body']
        )
        
        self.process_attachments(message)
        
        logger.info(f"Ticket {ticket.id} creado por usuario {self.request.user.username}")

        return render(self.request, 'ticket/success.html', {'ticket': ticket})

    def process_attachments(self, message):
        request = self.request
        attachment_count = 0
        
        while f'attachment-file-{attachment_count}' in request.FILES:
            file_key = f'attachment-file-{attachment_count}'
            name_key = f'attachment-name-{attachment_count}'
            
            if file_key in request.FILES and request.FILES[file_key]:
                uploaded_file = request.FILES[file_key]
                custom_name = request.POST.get(name_key, '').strip()
                filename = custom_name if custom_name else uploaded_file.name
                
                attachment = Attachment(
                    file=uploaded_file,
                    filename=filename,
                    message=message
                )
                attachment.save()
                
                logger.info(f"Archivo adjunto '{filename}' añadido al ticket {message.ticket.id}")

            attachment_count += 1

    def form_invalid(self, form):
        return render(self.request, 'ticket/create.html', {'form': form})


class TicketDetailView(LoginRequiredMixin, DetailView):
    model = Ticket
    template_name = 'ticket/view.html'
    context_object_name = 'ticket'
    pk_url_kwarg = 'ticket_id'

    def get_queryset(self):
        return Ticket.objects.get_queryset(user=self.request.user)
    
    def post(self, request, *args, **kwargs):

        ticket = self.get_object()
        
        message = Message.objects.create(
            ticket=ticket,
            status=request.POST.get('status', 'open'),
            user=request.user,
            body=request.POST.get('body', '')
        )
        
        self.process_attachments(request, message)

        logger.info(f"Respuesta enviada al ticket {ticket.id} por usuario {request.user.username} con estado {message.get_status_display()}")
        
        return redirect('ticket-list')
    
    def process_attachments(self, request, message):
        if 'attachment-highest-index' in request.POST:
            try:
                highest_index = int(request.POST.get('attachment-highest-index', '0'))
                for i in range(highest_index + 1):
                    file_key = f'attachment-file-{i}'
                    name_key = f'attachment-name-{i}'
                    if file_key in request.FILES and request.FILES[file_key]:
                        self.save_attachment(request, message, file_key, name_key)
            except ValueError:
                pass
        
        for key in request.FILES:
            if key.startswith('attachment-file-'):
                index = key.split('-')[-1]
                name_key = f'attachment-name-{index}'
                self.save_attachment(request, message, key, name_key)
    
    def save_attachment(self, request, message, file_key, name_key):
        uploaded_file = request.FILES[file_key]
        custom_name = request.POST.get(name_key, '').strip()
        filename = custom_name if custom_name else uploaded_file.name
        
        attachment = Attachment(
            file=uploaded_file,
            filename=filename,
            message=message
        )
        attachment.save()
        
        logger.info(
            "Archivo adjunto '{}' añadido a la respuesta en ticket {}",
            filename,
            message.ticket.id
        )


# ------------------------------------------------------------------------
# Partials
# ------------------------------------------------------------------------

@login_required(login_url='login')
def ticket_item_view(request, ticket_id):
    """
    Vista para mostrar un <article> con el ticket, en la lista de tickets.
    """
    ticket = get_object_or_404(Ticket, id=ticket_id)
    return render(request, 'ticket/partials/view/item-article.html', {
        'ticket': ticket
    })


@login_required(login_url='login')
def close_ticket(request, ticket_id):
    """
    Ejecuta la acción de cerrar un ticket (status: closed) luego de htmx-confirm-close.
    """
    if request.method == 'POST':
        ticket = get_object_or_404(Ticket, id=ticket_id)
        
        last_message = ticket.messages.last()

        Message.objects.create(
            ticket=ticket,
            status='closed',
            user=request.user
        )
        
        logger.info(f"Ticket {ticket.id} cerrado por usuario {request.user.username}")

        ticket.refresh_from_db()
        return render(request, 'ticket/partials/ticket-item.html', {'ticket': ticket})
