from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User, Group
from django.urls import reverse


class UDN(models.Model):
    """
    Unidad de Negocio (UDN) representa divisiones principales como sucursales o departamentos.
    
    Relaciones con grupos:
    - permission_group: Grupos con permisos administrativos sobre esta UDN (ej. "Administrative", "Administrativo").
      Estos grupos pueden gestionar la UDN desde el panel de administración.
    - groups: Grupos específicos asociados a esta UDN (ej. "UDN Km 1151", "UDN Las Bóvedas").
      Los usuarios en estos grupos pueden ver tickets de esta UDN.
    
    Ejemplo:
        udn_oficina = UDN.objects.get(name="Oficina Central")
        # Dar permiso administrativo al grupo "Administrative"
        admin_group = Group.objects.get(name="Administrative")
        udn_oficina.permission_group.add(admin_group)
        
        # Asociar el grupo específico "UDN Oficina Central"
        udn_group = Group.objects.get(name="UDN Oficina Central")
        udn_oficina.groups.add(udn_group)
    """
    name = models.CharField(max_length=255, verbose_name="Nombre")
    permission_group = models.ManyToManyField(Group, blank=True, related_name="udn_permissions", verbose_name="Grupos de Permisos")
    groups = models.ManyToManyField(Group, related_name='udns', blank=True)

    class Meta:
        verbose_name = "UDN"
        verbose_name_plural = "UDNs"

    def __str__(self):
        return self.name


class Sector(models.Model):
    """
    Sector representa áreas funcionales dentro de una UDN (por ejemplo, TI, RRHH, Finanzas).
    
    Relaciones con grupos:
    - permission_group: Grupos con permisos administrativos sobre este Sector (ej. "Administrative").
      Estos grupos pueden gestionar este Sector desde el panel de administración.
    - groups: Grupos específicos asociados a este Sector (ej. "SECTOR Playa", "SECTOR Parador").
      Los usuarios en estos grupos pueden ver tickets de este Sector.
    
    La combinación de permisos UDN+Sector define qué tickets puede ver un usuario.
    Un usuario debe tener acceso tanto a la UDN como al Sector para ver un ticket.
    
    Ejemplo:
        sector_ti = Sector.objects.get(name="TI")
        # Dar permiso administrativo al grupo "Administrative"
        admin_group = Group.objects.get(name="Administrative")
        sector_ti.permission_group.add(admin_group)
        
        # Asociar el grupo específico "SECTOR TI"
        sector_group = Group.objects.get(name="SECTOR TI")
        sector_ti.groups.add(sector_group)
    """
    udn = models.ManyToManyField(UDN, related_name="sectors", verbose_name="UDNs")
    name = models.CharField(max_length=255, verbose_name="Nombre")
    permission_group = models.ManyToManyField(Group, blank=True, related_name="sector_permissions", verbose_name="Grupos de Permisos")
    groups = models.ManyToManyField(Group, related_name='sectors_groups', blank=True)

    class Meta:
        verbose_name = "Sector"
        verbose_name_plural = "Sectores"

    def __str__(self):
        return self.name


class IssueCategory(models.Model):
    """
    Categoría de problemas asociada a sectores específicos.
    
    Relaciones con grupos:
    - permission_group: Grupos con permisos para gestionar esta categoría (ej. "Administrative").
      Estos grupos pueden administrar estas categorías desde el panel de administración.
    
    A diferencia de UDN y Sector, IssueCategory solo tiene permission_group, ya que no requiere
    grupos específicos para controlar la visibilidad (eso lo hacen UDN y Sector).
    
    Ejemplo:
        categoria_hardware = IssueCategory.objects.get(name="Hardware")
        # Dar permiso administrativo al grupo "IT Support"
        soporte_group = Group.objects.get(name="IT Support")
        categoria_hardware.permission_group.add(soporte_group)
    """
    name = models.CharField(max_length=255, verbose_name="Nombre")
    sector = models.ManyToManyField("Sector", related_name="issue_categories", verbose_name="Sectores")
    permission_group = models.ManyToManyField(Group, blank=True, related_name="category_permissions", verbose_name="Grupos de Permisos")

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.name


class Issue(models.Model):
    """
    Incidencia específica dentro de una categoría.
    
    Relaciones con grupos:
    - permission_group: Grupos con permisos para gestionar este tipo de incidencia (ej. "Soporte").
      Define qué grupos de usuarios pueden administrar este tipo de incidencia.
    
    Ejemplo:
        incidencia_pc = Issue.objects.get(name="PC no enciende")
        # Dar permiso administrativo al grupo "Soporte Técnico"
        soporte_group = Group.objects.get(name="Soporte Técnico")
        incidencia_pc.permission_group.add(soporte_group)
    """
    issue_category = models.ForeignKey(IssueCategory, on_delete=models.CASCADE, related_name="issues", verbose_name="Categoría")
    name = models.CharField(max_length=255, verbose_name="Nombre")
    display_name = models.CharField(max_length=255, verbose_name="Nombre a Mostrar", blank=True, null=True)
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    permission_group = models.ManyToManyField(Group, blank=True, related_name="issue_permissions", verbose_name="Grupos de Permisos")

    class Meta:
        verbose_name = "Incidencia"
        verbose_name_plural = "Incidencias"

    def __str__(self):
        return self.name


class TicketManager(models.Manager):
    """
    Gestor personalizado para el modelo Ticket que filtra automáticamente 
    los tickets según los permisos del usuario.
    
    La lógica de filtrado utiliza tanto permission_group como groups:
    - Un usuario puede ver tickets donde tiene permisos administrativos sobre la UDN o es miembro de un grupo asociado a ella
    - Y ADEMÁS tiene permisos administrativos sobre el Sector o es miembro de un grupo asociado a él
    
    Los superusuarios (is_superuser=True) pueden ver todos los tickets.
    
    Ejemplo:
        # En una vista:
        user = request.user
        visible_tickets = Ticket.objects.get_queryset(user=user)
        
        # Un usuario en el grupo "UDN Las Bóvedas" y "SECTOR Playa" verá solo
        # tickets de esa UDN y ese Sector
    """
    def get_queryset(self, user=None):
        queryset = super().get_queryset()
        if user and not user.is_superuser:
            return queryset.filter(
                (Q(udn__permission_group__in=user.groups.all()) | Q(udn__groups__in=user.groups.all())) &
                (Q(sector__permission_group__in=user.groups.all()) | Q(sector__groups__in=user.groups.all()))
            ).distinct()
        return queryset


class Ticket(models.Model):
    udn = models.ForeignKey(UDN, on_delete=models.CASCADE, verbose_name="UDN")
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, verbose_name="Sector")
    issue_category = models.ForeignKey(IssueCategory, on_delete=models.CASCADE, verbose_name="Categoría")
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, verbose_name="Incidencia")

    objects = TicketManager()  # Assign the custom manager

    class Meta:
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"

    def __str__(self):
        return self.issue.name

    def get_absolute_url(self):
        """Devuelve la URL para ver los detalles del ticket"""
        return reverse('ticket-view', kwargs={'ticket_id': self.id})

    def get_close_url(self):
        """Devuelve la URL para el endpoint de confirmación de cierre del ticket"""
        return reverse('htmx-confirm-close', kwargs={'ticket_id': self.id})

    @property
    def created_by(self):
        """Devuelve el usuario que creó el ticket (el primer mensaje)."""
        first_message = self.messages.order_by('created_on').first()
        return first_message.user if first_message else None

    @property
    def status(self):
        """Devuelve el estado actual del ticket (el estado del último mensaje)."""
        last_message = self.messages.order_by('-created_on').first()
        return last_message.status if last_message else None


class Message(models.Model):
    STATUS_CHOICES = [
        ('open', 'Abierto'),
        ('solved', 'Solucionado'),
        ('closed', 'Cerrado'),
        ('feedback', 'Comentado'),
    ]
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="messages", verbose_name="Ticket")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', verbose_name="Estado")
    reported_on = models.DateTimeField(null=True, blank=True, verbose_name="Fecha Reportada")
    created_on = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="messages", verbose_name="Usuario")
    body = models.TextField(verbose_name="Cuerpo del Mensaje", blank=True, null=True)


    class Meta:
        verbose_name = "Mensaje"
        verbose_name_plural = "Mensajes"
        ordering = ['created_on']

    def __str__(self):
        return f"Mensaje de {self.user.username} en {self.ticket.issue.name}"

    def save(self, *args, **kwargs):
        if self.reported_on is None:
          self.reported_on = self.created_on
        super().save(*args, **kwargs)


class Attachment(models.Model):
    file = models.FileField(upload_to="attachments/", verbose_name="Archivo")
    filename = models.CharField(max_length=255, verbose_name="Nombre del Archivo")
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="attachments", verbose_name="Mensaje", blank=True, null=True)

    class Meta:
        verbose_name = "Adjunto"
        verbose_name_plural = "Adjuntos"

    def __str__(self):
        return self.filename
