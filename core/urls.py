from django.urls import path
from . import views
from . import views_htmx

# URLs principales
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('development/', views.DevelopmentView.as_view(), name='development'),
    path('tickets/list/', views.TicketListView.as_view(), name='ticket-list'),
    path('tickets/view/<int:ticket_id>/item/', views.ticket_item_view, name='ticket-item'),
    path('tickets/view/<int:ticket_id>/', views.TicketDetailView.as_view(), name='ticket-view'),
    path('tickets/create/', views.CreateTicketView.as_view(), name='create-ticket'),
]

# URLs para selección con HTMX
urlpatterns += [
    path('htmx/create/udn/', views_htmx.htmx_udn, name='htmx-udn'),
    path('htmx/create/sector/<int:udn>/', views_htmx.htmx_sector, name='htmx-sector'),
    path('htmx/create/issue-category/<int:sector>/', views_htmx.htmx_issue_category, name='htmx-issue-category'),
    path('htmx/create/issue/<int:issue_category>/', views_htmx.htmx_issue, name='htmx-issue'),
    path('htmx/create/ticket-details/<int:issue>/', views_htmx.htmx_ticket_details, name='htmx-ticket-details'),
]

# URLs para operaciones HTMX adicionales
urlpatterns += [
    path('htmx/list-content/', views_htmx.htmx_list_content, name='htmx-list-content'),
    path('htmx/add-attachment/', views_htmx.htmx_add_attachment, name='htmx-add-attachment'),
    path('htmx/remove-attachment/', views_htmx.htmx_remove_attachment, name='htmx-remove-attachment'),
    path('htmx/confirm-close/<int:ticket_id>/', views_htmx.htmx_confirm_close_ticket, name='htmx-confirm-close'),
    path('tickets/<int:ticket_id>/close/', views.close_ticket, name='close-ticket'),
]
