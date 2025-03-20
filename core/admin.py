from django.contrib import admin
from django.utils.html import format_html, mark_safe
from django.template.defaultfilters import filesizeformat
import os

from .models import UDN, Sector, IssueCategory, Issue, Ticket, Message, Attachment


def get_permission_groups_display(obj):
    groups = obj.permission_group.all()
    if groups:
        links = [
            format_html(f'<a href="/admin/auth/group/{group.id}/change/">{group.name}</a>')
            for group in groups
        ]
        return mark_safe(", ".join(links))
    return "-"


@admin.register(UDN)
class UDNAdmin(admin.ModelAdmin):
    list_display = ("name", "display_permission_groups")
    list_filter = ("permission_group",)
    search_fields = ("name", "permission_group__name")
    filter_horizontal = ("permission_group",)
    ordering = ("name",)

    def display_permission_groups(self, obj):
        return get_permission_groups_display(obj)
    
    display_permission_groups.short_description = "Grupos de Permisos"


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ("name", "display_udns", "display_permission_groups")
    list_filter = ("udn", "permission_group")
    search_fields = ("name", "udn__name", "permission_group__name")
    autocomplete_fields = ("udn",)
    filter_horizontal = ("udn", "permission_group")
    ordering = ("name",)

    def display_udns(self, obj):
        return ", ".join([udn.name for udn in obj.udn.all()])
    
    display_udns.short_description = "UDNs"

    def display_permission_groups(self, obj):
        return get_permission_groups_display(obj)
    
    display_permission_groups.short_description = "Grupos de Permisos"


@admin.register(IssueCategory)
class IssueCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "display_permission_groups")
    list_filter = ("permission_group",)
    search_fields = ("name", "permission_group__name")
    filter_horizontal = ("permission_group",)
    ordering = ("name",)

    def display_permission_groups(self, obj):
        return get_permission_groups_display(obj)
    
    display_permission_groups.short_description = "Grupos de Permisos"


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ("name", "issue_category", "short_description", "display_permission_groups")
    list_filter = ("issue_category", "permission_group")
    search_fields = ("name", "description", "issue_category__name", "permission_group__name")
    autocomplete_fields = ("issue_category",)
    filter_horizontal = ("permission_group",)
    ordering = ("name",)

    def short_description(self, obj):
        return (
            obj.description[:50] + "..."
            if obj.description and len(obj.description) > 50
            else obj.description
        )

    short_description.short_description = "Descripción (Resumen)"
    
    def display_permission_groups(self, obj):
        return get_permission_groups_display(obj)
    
    display_permission_groups.short_description = "Grupos de Permisos"


class MessageInline(admin.TabularInline):
    model = Message
    readonly_fields = ('created_on',)
    extra = 0
    fields = ('status', 'reported_on', 'created_on', 'user', 'body')


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'udn', 'sector', 'issue_category', 'issue')
    list_filter = ('udn', 'sector', 'issue_category', 'issue')
    search_fields = ('udn__name', 'sector__name', 'issue_category__name', 'issue__name')
    inlines = [MessageInline]
    autocomplete_fields = ('udn', 'sector', 'issue_category', 'issue')


class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0
    fields = ('file', 'filename', 'file_preview', 'filesize')
    readonly_fields = ('file_preview', 'filesize')
    
    def file_preview(self, obj):
        if obj.file:
            filename = os.path.basename(obj.file.name)
            ext = os.path.splitext(filename)[1].lower()
            
            if ext in ['.jpg', '.jpeg', '.png', '.gif']:
                return format_html('<a href="{}" target="_blank"><img src="{}" width="100" /></a>', 
                                  obj.file.url, obj.file.url)
            elif ext == '.pdf':
                return format_html('<a href="{}" target="_blank"><img src="/static/admin/img/icon-pdf.svg" width="50" /> Ver PDF</a>', 
                                  obj.file.url)
            else:
                return format_html('<a href="{}" target="_blank">{}</a>', obj.file.url, filename)
        return "-"
    file_preview.short_description = "Vista previa"
    
    def filesize(self, obj):
        if obj.file and hasattr(obj.file, 'size'):
            return filesizeformat(obj.file.size)
        return "-"
    filesize.short_description = "Tamaño"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'status', 'reported_on', 'created_on', 'user', 'short_body', 'attachments_count')
    list_filter = ('status', 'reported_on', 'created_on', 'user')
    search_fields = ('body', 'user__username', 'ticket__issue__name')
    inlines = [AttachmentInline]
    autocomplete_fields = ('ticket', 'user')
    
    def short_body(self, obj):
        return (
            obj.body[:50] + "..."
            if obj.body and len(obj.body) > 50
            else obj.body
        )
    
    short_body.short_description = "Mensaje (Resumen)"
    
    def attachments_count(self, obj):
        count = obj.attachments.count()
        if count > 0:
            return format_html('<span style="background-color: #e4f0e8; padding: 3px 8px; border-radius: 10px;">{}</span>', count)
        return "-"
    attachments_count.short_description = "Adjuntos"


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('filename', 'message', 'file_preview_thumbnail', 'filesize')
    list_filter = ('message__ticket',)
    search_fields = ('filename', 'message__body', 'message__ticket__issue__name')
    autocomplete_fields = ('message',)
    readonly_fields = ('file_preview', 'filesize')
    fields = ('file', 'filename', 'message', 'file_preview', 'filesize')
    
    def file_preview(self, obj):
        if obj.file:
            filename = os.path.basename(obj.file.name)
            ext = os.path.splitext(filename)[1].lower()
            
            if ext in ['.jpg', '.jpeg', '.png', '.gif']:
                return format_html('<a href="{}" target="_blank"><img src="{}" width="300" /></a>', 
                                  obj.file.url, obj.file.url)
            elif ext == '.pdf':
                return format_html('<a href="{}" target="_blank"><img src="/static/admin/img/icon-pdf.svg" width="100" /><br>Ver PDF</a>', 
                                  obj.file.url)
            else:
                file_icon = "icon-unknown.svg"
                if ext in ['.doc', '.docx']:
                    file_icon = "icon-doc.svg"
                elif ext in ['.xls', '.xlsx']:
                    file_icon = "icon-xls.svg"
                elif ext in ['.txt']:
                    file_icon = "icon-txt.svg"
                
                return format_html('<a href="{}" target="_blank"><img src="/static/admin/img/{}" width="50" /><br>{}</a>', 
                                  obj.file.url, file_icon, filename)
        return "-"
    file_preview.short_description = "Vista previa"
    
    def file_preview_thumbnail(self, obj):
        if obj.file:
            filename = os.path.basename(obj.file.name)
            ext = os.path.splitext(filename)[1].lower()
            
            if ext in ['.jpg', '.jpeg', '.png', '.gif']:
                return format_html('<a href="{}" target="_blank"><img src="{}" width="50" /></a>', 
                                  obj.file.url, obj.file.url)
            elif ext == '.pdf':
                return format_html('<a href="{}" target="_blank"><img src="/static/admin/img/icon-pdf.svg" width="30" /></a>', 
                                  obj.file.url)
            else:
                return format_html('<a href="{}" target="_blank"><span class="material-icons">attachment</span></a>', 
                                  obj.file.url)
        return "-"
    file_preview_thumbnail.short_description = "Vista previa"
    
    def filesize(self, obj):
        if obj.file and hasattr(obj.file, 'size'):
            return filesizeformat(obj.file.size)
        return "-"
    filesize.short_description = "Tamaño"
