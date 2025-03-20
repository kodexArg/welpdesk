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
    template_name = 'home.html'


class TicketListView(LoginRequiredMixin, TemplateView):
    template_name = 'ticket/ticket-list.html'  
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Si el usuario es staff, o está en el grupo 'Auditor' o 'Soporte', mostrar todos los tickets
        if self.request.user.is_staff or self.request.user.groups.filter(name__in=['Auditor', 'Support']).exists():
            tickets = Ticket.objects.annotate(
                last_message_timestamp=models.Max('messages__created_on')
            ).order_by('-last_message_timestamp')
        else:
            # Para usuarios normales, mostrar solo sus propios tickets
            tickets = Ticket.objects.filter(
                messages__user=self.request.user,
                messages__id=models.Subquery(
                    Message.objects.filter(
                        ticket=models.OuterRef('pk')
                    ).order_by('created_on').values('id')[:1]
                )
            ).annotate(
                last_message_timestamp=models.Max('messages__created_on')
            ).order_by('-last_message_timestamp').distinct()
        
        # Configurar el paginador
        page_number = self.request.GET.get('page')
        paginator = Paginator(tickets, 10) 
        page_obj = paginator.get_page(page_number)
        
        context['page_obj'] = page_obj
        context['tickets'] = page_obj.object_list
        
        return context


@login_required(login_url='login')
def ticket_item_view(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    return render(request, 'ticket/partials/ticket-item.html', {
        'ticket': ticket
    })


class CreateTicketView(LoginRequiredMixin, FormView):
    template_name = 'ticket/ticket-new.html' 
    form_class = TicketCreationForm
    login_url = 'login'  
    
    def form_valid(self, form):
        """Procesa el formulario válido, creando el Ticket y su primer Message."""
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
        
        groups = [group.name for group in self.request.user.groups.all()]
        logger.info(
            "Ticket {} creado por usuario {} (Grupos: {})",
            ticket.id,
            self.request.user.username,
            ', '.join(groups) if groups else "Sin grupos"
        )
        
        return render(self.request, 'ticket/success.html', {'ticket': ticket})

    def process_attachments(self, message):
        """Procesa y guarda los archivos adjuntos asociados al mensaje."""
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
                
                logger.info(
                    "Archivo adjunto '{}' añadido al ticket {}",
                    filename,
                    message.ticket.id
                )
            
            attachment_count += 1

    def form_invalid(self, form):
        """Maneja el caso en que el formulario tiene errores."""
        return render(self.request, 'ticket/ticket-new.html', {'form': form})  # Updated template name

@login_required(login_url='login')
def htmx_udn(request):
    # Si el usuario es staff, mostrar todas las UDNs
    if request.user.is_staff:
        udns = UDN.objects.all()
    else:
        user_groups = request.user.groups.all()
        udns = UDN.objects.filter(
            models.Q(permission_group__in=user_groups) | 
            models.Q(groups__in=user_groups)
        ).distinct()
    
    return render(request, 'ticket/partials/udn.html', {'udns': udns})


@login_required(login_url='login')
def htmx_sector(request, udn):
    # Obtener el objeto UDN
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
    
    return render(request, 'ticket/partials/sector.html', {'sectors': sectors})


@login_required(login_url='login')
def htmx_issue_category(request, sector):
    issue_categories = IssueCategory.objects.filter(sector__id=sector)
    return render(request, 'ticket/partials/issue-category.html', {'issue_categories': issue_categories})


@login_required(login_url='login')
def htmx_issue(request, issue_category):
    issues = Issue.objects.filter(issue_category=issue_category)
    return render(request, 'ticket/partials/issue.html', {'issues': issues})

@login_required(login_url='login')
def htmx_ticket_details(request, issue):
    """Render the ticket details form section."""
    # Obtener el objeto Issue
    issue_obj = get_object_or_404(Issue, id=issue)
    
    # Pasar el issue al contexto de la plantilla
    return render(request, 'ticket/partials/ticket-details.html', {
        'issue': issue_obj
    })

@login_required(login_url='login')
def htmx_add_attachment(request):
    """
    Endpoint HTMX para agregar un nuevo componente de adjunto.
    Devuelve un nuevo formulario de adjunto con un índice incrementado.
    """
    # Inicializa el índice máximo encontrado a -1
    max_index = -1
    
    if request.method == 'POST':
        # Primero, verifica si existe un campo que indica el índice más alto
        if 'attachment-highest-index' in request.POST:
            try:
                # Intenta obtener el valor del índice más alto desde el request POST
                max_index = int(request.POST.get('attachment-highest-index', '-1'))
            except ValueError:
                # Si el valor no es un entero válido, ignora el error
                pass
            
        # Luego, revisa todos los campos de adjuntos en el request POST para encontrar el índice más alto
        for key in request.POST:
            if key.startswith('attachment-file-') or key.startswith('attachment-name-'):
                try:
                    # Extrae el índice del nombre del campo
                    index = int(key.split('-')[-1])
                    # Actualiza el índice máximo si el índice actual es mayor
                    max_index = max(max_index, index)
                except ValueError:
                    # Si el valor no es un entero válido, ignora el error
                    pass
        
        # También revisa los inputs de tipo archivo que pueden estar en FILES pero no en POST
        for key in request.FILES:
            if key.startswith('attachment-file-'):
                try:
                    # Extrae el índice del nombre del campo
                    index = int(key.split('-')[-1])
                    # Actualiza el índice máximo si el índice actual es mayor
                    max_index = max(max_index, index)
                except ValueError:
                    # Si el valor no es un entero válido, ignora el error
                    pass
    
    # Incrementa el índice para el nuevo adjunto
    new_index = max_index + 1
    
    # Imprime el cálculo del índice para depuración
    print(f"Agregando nuevo adjunto con índice: {new_index} (máximo encontrado: {max_index})")
    
    # Renderiza la plantilla con el nuevo índice
    return render(request, 'ticket/partials/attachment-item.html', {
        'index': new_index
    })

@login_required(login_url='login')
def htmx_remove_attachment(request):
    """
    Endpoint HTMX para eliminar un adjunto.
    Devuelve una respuesta vacía para eliminar completamente el elemento del adjunto.
    """
    return HttpResponse('')

class TicketDetailView(LoginRequiredMixin, DetailView):
    """Class based view for displaying ticket details and handling responses."""
    model = Ticket
    template_name = 'ticket/ticket-view.html'
    context_object_name = 'ticket'
    pk_url_kwarg = 'ticket_id'
    login_url = 'login'
    
    def post(self, request, *args, **kwargs):
        """Handle form submissions for ticket responses."""
        ticket = self.get_object()
        
        # Create a new message associated with the ticket
        message = Message.objects.create(
            ticket=ticket,
            status=request.POST.get('status', 'open'),
            user=request.user,
            body=request.POST.get('body', '')
        )
        
        # Process attachments
        self.process_attachments(request, message)
        
        logger.info(
            "Respuesta enviada al ticket {} por usuario {} con estado {}",
            ticket.id,
            request.user.username,
            message.get_status_display()
        )
        
        # Redirección a la lista de tickets en lugar de volver al detalle
        return redirect('ticket-list')
    
    def process_attachments(self, request, message):
        """Procesa y guarda los archivos adjuntos asociados al mensaje."""
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
                
                logger.info(
                    "Archivo adjunto '{}' añadido a la respuesta en ticket {}",
                    filename,
                    message.ticket.id
                )
            
            attachment_count += 1

@login_required(login_url='login')
def htmx_confirm_close_ticket(request, ticket_id):
    """Muestra el modal de confirmación para cerrar un ticket."""
    ticket = get_object_or_404(Ticket, id=ticket_id)
    return render(request, 'ticket/partials/modal-confirm.html', {'ticket': ticket})

@login_required(login_url='login')
def close_ticket(request, ticket_id):
    """Cierra un ticket creando un mensaje final con estado cerrado."""
    if request.method == 'POST':
        ticket = get_object_or_404(Ticket, id=ticket_id)
        
        # Verificar si el ticket ya está cerrado
        last_message = ticket.messages.last()
        if last_message and last_message.status == 'closed':
            logger.info(
                "Ticket {} ya está cerrado - solicitud ignorada",
                ticket.id
            )
        else:
            # Crear mensaje de cierre
            Message.objects.create(
                ticket=ticket,
                status='closed',
                user=request.user
            )
            
            logger.info(
                "Ticket {} cerrado por usuario {}",
                ticket.id,
                request.user.username
            )
        
        # Actualiza ticket desde base de datos para garantizar datos frescos
        ticket.refresh_from_db()
        
        # Devolver el ticket actualizado
        return render(request, 'ticket/partials/ticket-item.html', {'ticket': ticket})
