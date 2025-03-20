from django_components import component

@component.register("brand-logo")
class BrandLogo(component.Component):
    template_name = "brand-logo/brand-logo.html"
    
    def get_context_data(self):
        return {}  # Sin parámetros
    