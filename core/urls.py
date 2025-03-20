from django.urls import path
from . import views

# URLs principales
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('tickets/', views.TicketListView.as_view(), name='ticket-list'),
    path('tickets/<int:ticket_id>/item/', views.ticket_item_view, name='ticket-item'),
    path('tickets/<int:ticket_id>/', views.TicketDetailView.as_view(), name='ticket-view'),
    path('ticket/new/', views.CreateTicketView.as_view(), name='create-ticket'),
]

# URLs para selección con HTMX
urlpatterns += [
    path('htmx/udn/', views.htmx_udn, name='htmx-udn'),
    path('htmx/sector/<int:udn>/', views.htmx_sector, name='htmx-sector'),
    path('htmx/issue-category/<int:sector>/', views.htmx_issue_category, name='htmx-issue-category'),
    path('htmx/issue/<int:issue_category>/', views.htmx_issue, name='htmx-issue'),
    path('htmx/ticket-details/<int:issue>/', views.htmx_ticket_details, name='htmx-ticket-details'),
]

# URLs para operaciones HTMX adicionales
urlpatterns += [
    path('htmx/add-attachment/', views.htmx_add_attachment, name='htmx-add-attachment'),
    path('htmx/remove-attachment/', views.htmx_remove_attachment, name='htmx-remove-attachment'),
    path('htmx/confirm-close/<int:ticket_id>/', views.htmx_confirm_close_ticket, name='htmx-confirm-close'),
    path('tickets/<int:ticket_id>/close/', views.close_ticket, name='close-ticket'),
]
