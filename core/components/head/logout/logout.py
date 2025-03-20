from django_components import component

@component.register("logout")
class Logout(component.Component):
    template_name = "logout/logout.html"
    
    def get_context_data(self, user=None):
        return {
            'user': user  # opcional: (objeto) usuario actual logueado
        } 