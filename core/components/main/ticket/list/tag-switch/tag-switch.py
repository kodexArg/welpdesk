from django_components import component

@component.register("tag-switch")
class TagSwitch(component.Component):
    template_name = "main/ticket/list/tag-switch/tag-switch.html"
    
    def get_context_data(
        self,
        label,
        type="udn",
        name=None,
        value=None,
        checked=False,
        hx_get=None,
        hx_target=None,
        hx_swap=None,
        hx_trigger=None,
        hx_include=None,
        hx_vals=None,
    ):
        """
        Devuelve el contexto para el componente tag-switch.
        
        Args:
            label (str): El texto que se mostrará en el interruptor
            type (str): El tipo de etiqueta (udn, sector, category)
            name (str): El nombre del campo para el formulario
            value (str): El valor del interruptor cuando está activado
            checked (bool): Si el interruptor está activado por defecto
            hx_get (str, optional): URL para la petición GET de HTMX. Por defecto None.
            hx_target (str, optional): Selector CSS para el objetivo de HTMX. Por defecto None.
            hx_swap (str, optional): Estrategia de intercambio de HTMX. Por defecto None.
            hx_trigger (str, optional): Evento que dispara la petición HTMX. Por defecto None.
            hx_include (str, optional): Selectores CSS para incluir en la petición HTMX. Por defecto None.
            hx_vals (str, optional): Valores de HTMX. Por defecto None.
        """
        return {
            'label': label,            # Texto visible del switch
            'type': type,              # Tipo de etiqueta (udn, sector, category)
            'name': name or label,     # Nombre del campo (para formularios)
            'value': value or label,   # Valor cuando está activado
            'checked': checked,        # Estado inicial (activado/desactivado)
            'hx_get': hx_get,          # URL de HTMX GET
            'hx_target': hx_target,    # Objetivo de HTMX
            'hx_swap': hx_swap,        # Estrategia de intercambio de HTMX
            'hx_trigger': hx_trigger,  # Evento de disparo de HTMX
            'hx_include': hx_include,  # Selectores CSS de HTMX para incluir
            'hx_vals': hx_vals,        # Valores de HTMX
        }