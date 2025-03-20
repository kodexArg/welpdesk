from django_components import component

@component.register("separator")
class Separator(component.Component):
    template_name = "separator/separator.html"
    
    def get_context_data(self, custom_classes=""):
        return {
            "custom_classes": custom_classes  # opcional: (str) clases CSS adicionales
        } 