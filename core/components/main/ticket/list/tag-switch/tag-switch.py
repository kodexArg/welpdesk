from django_components import component

@component.register("tag-switch")
class TagSwitch(component.Component):
    template_name = "main/ticket/list/tag-switch/tag-switch.html"
    
    def get_context_data(self, label, type="udn", name=None, value=None, checked=False):
        """
        Devuelve el contexto para el componente tag-switch.
        
        Args:
            label (str): El texto que se mostrará en el interruptor
            type (str): El tipo de etiqueta (udn, sector, category)
            name (str): El nombre del campo para el formulario
            value (str): El valor del interruptor cuando está activado
            checked (bool): Si el interruptor está activado por defecto
        """
        return {
            'label': label,          # Texto visible del switch
            'type': type,            # Tipo de etiqueta (udn, sector, category)
            'name': name or label,   # Nombre del campo (para formularios)
            'value': value or label, # Valor cuando está activado
            'checked': checked       # Estado inicial (activado/desactivado)
        }