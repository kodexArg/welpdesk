
# Welp Desk

[![GitHub](https://img.shields.io/badge/GitHub-kodexArg-blue?style=flat&logo=github)](https://github.com/kodexArg/welpdesk)

Sistema de ticketing para mesa de ayuda basado en Django 5. Altamente configurable y fácil de personalizar para adaptarse a las necesidades específicas de cualquier organización con múltiples unidades de negocio.

## Características principales

- **Arquitectura multi-organizacional** con soporte para múltiples niveles jerárquicos (UDNs, Sectores)
- **Categorización jerárquica** de incidencias para una clasificación precisa
- **Sistema de permisos granular** basado en grupos de Django para control de acceso avanzado
- **Interfaz reactiva** utilizando Django Templates con HTMX para actualizaciones parciales
- **Gestión completa del ciclo de vida** de tickets con seguimiento de estados
- **Filtrado avanzado** por UDN, Sector, Categoría y Estado de tickets
- **Soporte para mensajes múltiples** en cada ticket, incluido historial completo
- **Adjuntos de archivos** en cada mensaje con validación de tamaño
- **Containerizado** con Docker para despliegue simplificado en cualquier entorno
- **Arquitectura escalable** optimizada para entornos empresariales

## Arquitectura técnica

### Tecnologías principales

- **Django 5**: Framework web de alto nivel con ORM integrado para modelos de datos complejos
- **PostgreSQL 16**: Sistema de base de datos relacional para almacenamiento persistente
- **HTMX**: Biblioteca que permite actualizaciones parciales de la interfaz sin JavaScript complejo
- **Vite**: Sistema moderno de empaquetado y desarrollo para activos frontend
- **Tailwind CSS**: Framework CSS utilitario para diseño rápido y consistente
- **Docker & Docker Compose**: Plataforma de contenedores para entornos aislados y reproducibles
- **Gunicorn**: Servidor WSGI de alto rendimiento para aplicaciones Python
- **Nginx**: Servidor web de alto rendimiento y proxy inverso para servir activos estáticos

### Modelo de datos para entornos multi-organizacionales

El sistema implementa una estructura altamente flexible diseñada para adaptarse a cualquier jerarquía organizacional:

- **UDN (Unidad de Negocio)**: Representa divisiones principales como sucursales, departamentos, o unidades de negocio independientes, cada una con sus propias configuraciones y permisos.
- **Sector**: Áreas funcionales dentro de cada UDN, permitiendo una subdivisión organizacional detallada (ej. TI, RRHH, Finanzas).
- **IssueCategory**: Clasificación principal de tipos de problemas asociados a sectores específicos.
- **Issue**: Tipos específicos de problemas dentro de cada categoría, configurables según las necesidades.
- **Ticket**: Entidad central que registra incidencias, vinculada a UDN, Sector, Categoría e Issue específicos.
- **Message**: Sistema de seguimiento de comunicaciones con registro de estados y cambios.
- **Attachment**: Soporte para adjuntos en cada mensaje con validación de tamaño.

Este modelo permite una implementación que se adapta desde pequeñas empresas hasta grandes corporaciones con múltiples unidades de negocio distribuidas geográficamente.

## Sistema avanzado de tickets para entornos empresariales

### Gestión de estados y ciclo de vida

El sistema ofrece un flujo de trabajo completo con estados configurables:
- **Abierto**: Tickets recién creados que requieren atención
- **En comentarios**: Tickets en proceso de discusión
- **Solucionado**: Tickets con resolución propuesta
- **Cerrado**: Tickets finalizados

La transición entre estados está controlada por permisos granulares basados en roles de usuario.

### Implementación técnica de mensajes y adjuntos

Cada ticket funciona como un hilo de conversación, donde:
- Los mensajes están vinculados al ticket y registran cambios de estado
- Cada mensaje puede contener múltiples adjuntos con validación de tamaño (hasta 50MB)
- El sistema registra automáticamente metadatos (fecha, hora, usuario, estado)

## Sistema de filtrado dinámico con HTMX

La vista `TicketListView` implementa un sistema de filtrado avanzado mediante HTMX:

- **Filtros en tiempo real**: La interfaz se actualiza dinámicamente sin recargar la página completa
- **Filtrado por UDN, Sector, Categoría y Estado**: Permite refinamientos precisos de los tickets visibles
- **Filtros persistentes vía URL**: Los parámetros de filtro se mantienen en la URL, permitiendo compartir vistas filtradas
- **Optimización de consultas**: Implementación eficiente con anotaciones y subconsultas para un rendimiento óptimo

### Implementación técnica del filtrado:

```python
# Extracto de views.py mostrando el sistema de filtrado
def get_context_data(self, **kwargs):
    # Obtiene filtros activos de la URL
    current_filters = {
        'udn': set(self.request.GET.getlist('udn')),
        'sector': set(self.request.GET.getlist('sector')),
        'category': set(self.request.GET.getlist('category')),
        'status': set(self.request.GET.getlist('status')),
    }
    
    # Implementación de permisos basados en usuario
    permitted_tickets = Ticket.objects.all() if self.request.user.is_staff else Ticket.objects.get_queryset(user=self.request.user).distinct()
    
    # Filtrado avanzado con subconsultas para estado de ticket
    if 'status' in self.request.GET:
        statuses = self.request.GET.getlist('status')
        last_message_ids = Message.objects.filter(ticket=models.OuterRef('pk')).order_by('-created_on').values('pk')[:1]
        queryset = queryset.filter(messages__pk__in=models.Subquery(last_message_ids), messages__status__in=statuses)
```

## Despliegue con Docker en entornos empresariales

El sistema está completamente containerizado, facilitando su despliegue en cualquier infraestructura:

```yaml
# docker-compose.yaml
services:
  db:
    image: postgres:16
    env_file:
      - .env
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 2s
      timeout: 1s
      retries: 5

  web:
    build:
      context: .
      dockerfile: Dockerfile
    command: >
      bash -c "python manage.py collectstatic --noinput &&
               python manage.py migrate &&
               gunicorn project.wsgi:application --bind 0.0.0.0:80 --workers=3 --threads=2 --max-requests=2000 --max-requests-jitter=200"
    volumes:
      - staticfiles:/app/staticfiles
      - mediafiles:/app/mediafiles

  nginx:
    image: nginx:1.25.3
    volumes:
      - ./configs/nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - staticfiles:/staticfiles:ro
      - mediafiles:/mediafiles:ro
    ports:
      - "80:80"
```

### Configuración para entornos de producción

El proyecto utiliza variables de entorno para una configuración flexible en diferentes entornos:

```
# Ejemplo de archivo .env (usar valores propios en producción)
SECRET_KEY=your_secure_random_key_here
DEBUG=False

POSTGRES_DB=welpdesk_prod
POSTGRES_USER=welpdesk_user
POSTGRES_PASSWORD=secure_password_here
POSTGRES_HOST=db
POSTGRES_PORT=5432

ALLOWED_HOSTS=your-domain.com,www.your-domain.com
SERVER_NAME=your-domain.com

LANGUAGE_CODE=es-AR
TIME_ZONE=America/Argentina/Buenos_Aires
```

## Estructura del proyecto y enrutamiento

El sistema implementa un patrón de diseño modular con separación de responsabilidades:

```python
# Extracto de urls.py
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('tickets/list/', views.TicketListView.as_view(), name='ticket-list'),
    path('tickets/view/<int:ticket_id>/', views.TicketDetailView.as_view(), name='ticket-view'),
    path('tickets/create/', views.CreateTicketView.as_view(), name='create-ticket'),
]

# URLs para selección con HTMX
urlpatterns += [
    path('htmx/create/udn/', views_htmx.htmx_udn, name='htmx-udn'),
    path('htmx/create/sector/<int:udn>/', views_htmx.htmx_sector, name='htmx-sector'),
    # ...y más endpoints HTMX
]
```

## Instalación y despliegue

### Requisitos previos
- Docker y Docker Compose
- Acceso a entorno Linux/Unix recomendado para producción

### Pasos para instalación

1. Clone el repositorio:
   ```bash
   git clone https://github.com/kodexArg/welpdesk.git
   cd welpdesk
   ```

2. Configure el archivo .env (puede basarse en .env.example):
   ```bash
   cp .env.example .env
   # Edite los valores según su entorno
   ```

3. Inicie los servicios con Docker Compose:
   ```bash
   docker-compose up -d
   ```

4. Cree un superusuario administrativo:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

El sistema estará disponible en http://localhost (o el puerto configurado).

## Personalización para necesidades específicas

Welp Desk puede adaptarse a la estructura organizativa de cualquier empresa modificando:

- Modelos UDN y Sector para reflejar la jerarquía organizacional
- Categorías y tipos de incidencias según requisitos específicos
- Flujos de trabajo y estados según procedimientos internos
- Roles y permisos alineados con la estructura organizacional

## Contribuciones y soporte

Desarrollado por [Gabriel Cavedal](https://github.com/kodexArg)

Las contribuciones son bienvenidas. Para contribuir:

1. Haga un fork del repositorio
2. Cree una rama para su funcionalidad (`git checkout -b feature/amazing-feature`)
3. Confirme sus cambios (`git commit -m 'Añadir funcionalidad increíble'`)
4. Empuje la rama (`git push origin feature/amazing-feature`)
5. Abra un Pull Request en GitHub

## Licencia

Este proyecto está bajo la Licencia MIT - vea el archivo LICENSE.md para más detalles.
