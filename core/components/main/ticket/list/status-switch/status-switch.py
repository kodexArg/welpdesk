from django_components import component

@component.register("status-switch")
class StatusSwitch(component.Component):
    template_name = "main/ticket/list/status-switch/status-switch.html"

    def get_context_data(self, status, checked=False, hx_get=None, hx_target=None, hx_swap=None, hx_trigger=None, hx_include=None, hx_vals=None):
        # Validar que el estado sea uno de los permitidos
        if status not in ['open', 'solved', 'closed', 'feedback']:
            raise ValueError("Estado de ticket inválido en status-switch")

        # Diccionario para mapear estados a iconos
        icon_map = {
            'open': 'fa-exclamation-circle',
            'solved': 'fa-wrench',
            'closed': 'fa-check-circle',
            'feedback': 'fa-comment',
        }

        return {
            'status': status,  # 'open', 'solved', 'closed', 'feedback'
            'checked': checked,
            'icon': icon_map[status],  # Añadir el icono al contexto
            'hx_get': hx_get,
            'hx_target': hx_target,
            'hx_swap': hx_swap,
            'hx_trigger': hx_trigger,
            'hx_include': hx_include,
            'hx_vals': hx_vals,
        }