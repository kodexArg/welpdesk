from django_components import component
from django.urls import reverse

@component.register("radio-button")
class RadioButton(component.Component):
    template_name = "main/ticket/new/radio-button/radio-button.html"
    
    def get_context_data(self, target, id, label, next_target, visible=True):
        url_name = f'htmx-{next_target}'
        url_kwargs = {target: id}
        full_url = reverse(url_name, kwargs=url_kwargs)

        return {
            'target': target,               # (str) nombre del grupo de radio buttons
            'id': id,                       # (int) ID único del radio button
            'value': id,                    # (int) valor del radio button, igual al id
            'label': label,                 # (str) texto visible del radio button
            'next_target': next_target,     # (str) siguiente target en la cadena
            'full_url': full_url,           # URL completa ya procesada con reverse
            'visible': visible,             # (bool) controla si el componente es visible
        } 