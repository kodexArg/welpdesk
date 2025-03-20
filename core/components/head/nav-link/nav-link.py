from django_components import component

@component.register("nav-link")
class NavLink(component.Component):
    template_name = "nav-link/nav-link.html"
    
    def get_context_data(self, link, icon, label, current_view=None, always_show_label=False):
        active = False
        if current_view:
            active = link == current_view
            
        return {
            'link': link,                  # (str) URL del enlace
            'icon': icon,                  # (str) clase de icono
            'label': label,                # (str) texto del enlace
            'active': active,              # (bool) si el enlace está activo
            'always_show_label': always_show_label,
        }