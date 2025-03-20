from django_components import component
from django.contrib.auth.models import Group

@component.register("button")
class Button(component.Component):
    template_name = "button/button.html"
    
    # Lista de clases de botones válidas
    VALID_BUTTON_CLASSES = [
        'button-primary', 'button-secondary', 'button-success', 'button-danger', 'button-cancel',
        'button-outline-primary', 'button-outline-secondary', 'button-outline-success', 
        'button-outline-danger', 'button-outline-cancel'
    ]
    
    def get_context_data(self, 
                         label, 
                         action="#", 
                         id=None,
                         icon=None, 
                         disabled=False,
                         target=None,
                         color=None,
                         text_color=None,
                         cancel=False,
                         permissions=None):

        is_submit = action == "#" or action == "submit"
        
        # Determinar la clase de color del botón
        if cancel and not color:
            color = 'button-cancel'
        
        # Validar si el color es una clase válida, si no usar button-primary
        if not color or color not in self.VALID_BUTTON_CLASSES:
            color = 'button-primary'
        
        # Construir la clase CSS completa
        css_class = color
        
        if icon:
            css_class += ' button-icon'
            
        if text_color:
            css_class += f' {text_color}'
        
        # Determinar el tipo de acción HTMX
        htmx_attrs = {}
        if not is_submit and action and action != "#":
            htmx_attrs['hx-get'] = action
            htmx_attrs['hx-target'] = target if target else "body"
        
        if not disabled:
            if permissions:
                # Obtener el usuario actual del contexto de la solicitud
                request = self.context.get('request')
                user = request.user if request else None
                
                # Inicialmente asumimos que el usuario no tiene permisos
                has_permission = False
                
                # Verificar si el usuario pertenece a alguno de los grupos permitidos
                if user and user.is_authenticated:
                    user_groups = set(group.name for group in user.groups.all())
                    allowed_groups = set(permissions)

                    if user_groups.intersection(allowed_groups):
                        has_permission = True
                
                # Si el usuario no tiene permiso, deshabilitar el botón
                # independientemente del valor original de disabled
                if not has_permission:
                    disabled = True
        
        return {
            'label': label,                # (str) texto del botón
            'icon': icon,                  # opcional: (str) clase de icono
            'is_submit': is_submit,        # (bool) si es botón de tipo submit
            'action': action if not is_submit else "#",  # (str) URL de acción HTMX 
            'id': id,                      # opcional: (str) ID del botón
            'disabled': bool(disabled),    # (bool) si el botón está deshabilitado
            'target': target,              # opcional: (str) selector objetivo HTMX
            'css_class': css_class,        # (str) clases CSS completas
            'htmx_attrs': htmx_attrs       # (dict) atributos HTMX
        } 