from django.apps import AppConfig
from django.db.models.signals import post_migrate
import os
import yaml
from .logger import logger
from django.db import transaction


class CoreConfig(AppConfig):
    name = "core"

    def ready(self):
        # Asegurar que create_superuser se ejecute antes de las operaciones de modelo
        post_migrate.connect(self.create_superuser, sender=self)
        post_migrate.connect(self.setup_groups_and_permissions, sender=self)
        post_migrate.connect(self.populate_db, sender=self)
        # create_model_groups se moverá dentro de populate_db

    def setup_groups_and_permissions(self, sender, **kwargs):
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType

        groups = self.create_default_groups()

        self.assign_auditor_permissions(groups.get("Auditor"), ContentType, Permission)
        self.assign_operator_permissions(
            groups.get("Operator"), ContentType, Permission
        )
        self.assign_support_permissions(groups.get("Support"), ContentType, Permission)
        self.assign_administrative_permissions(
            groups.get("Administrative"), ContentType, Permission
        )

    def create_default_groups(self):
        from django.contrib.auth.models import Group

        groups = {}
        group_names = ["Operator", "Auditor", "Support", "Administrative"]

        for group_name in group_names:
            group, created = Group.objects.get_or_create(name=group_name)
            groups[group_name] = group

        return groups

    def assign_permissions(self, group, permissions_config, ContentType, Permission):
        if not group:
            return

        for model_name, permission_types in permissions_config.items():
            try:
                content_type = ContentType.objects.get(model=model_name.lower())

                for permission_type in permission_types:
                    codename = f"{permission_type}_{model_name.lower()}"
                    try:
                        permission = Permission.objects.get(
                            codename=codename, content_type=content_type
                        )
                        group.permissions.add(permission)
                    except Permission.DoesNotExist:
                        print(f"Permiso no encontrado: {codename}")

            except ContentType.DoesNotExist:
                print(f"Modelo no encontrado: {model_name}")

    def assign_auditor_permissions(self, group, ContentType, Permission):
        permissions_config = {
            "udn": ["view"],
            "sector": ["view"],
            "issuecategory": ["view"],
            "issue": ["view"],
            "ticket": ["view"],
            "message": ["view", "add"],
        }

        self.assign_permissions(group, permissions_config, ContentType, Permission)

    def assign_operator_permissions(self, group, ContentType, Permission):
        permissions_config = {
            "udn": ["view"],
            "sector": ["view"],
            "issuecategory": ["view"],
            "issue": ["view"],
            "ticket": ["view", "add"],
            "message": ["view", "add"],
        }

        self.assign_permissions(group, permissions_config, ContentType, Permission)

    def assign_administrative_permissions(self, group, ContentType, Permission):
        # Mismo conjunto de permisos que Operator
        permissions_config = {
            "udn": ["view"],
            "sector": ["view"],
            "issuecategory": ["view"],
            "issue": ["view"],
            "ticket": ["view", "add"],
            "message": ["view", "add"],
        }

        self.assign_permissions(group, permissions_config, ContentType, Permission)

    def assign_support_permissions(self, group, ContentType, Permission):
        permissions_config = {
            "udn": ["view"],
            "sector": ["view"],
            "issuecategory": ["view"],
            "issue": ["view"],
            "ticket": ["view"],
            "message": ["view", "add"],
        }

        self.assign_permissions(group, permissions_config, ContentType, Permission)

    def load_yaml_data(self):
        yaml_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'configs', 'initialize-db', 'initialize-db.yaml')
        try:
            with open(yaml_file_path, 'r') as file:
                data = yaml.safe_load(file)
            logger.info("Datos YAML cargados exitosamente desde {}", yaml_file_path)
            return data
        except FileNotFoundError:
            logger.error("Archivo YAML no encontrado en: {}", yaml_file_path)
            return None
        except yaml.YAMLError as e:
            logger.error("Error al parsear el archivo YAML: {}", e)
            return None

    def populate_db(self, sender, **kwargs):
        from .models import UDN, Sector, IssueCategory, Issue

        logger.info("Iniciando población de la base de datos...")
        data = self.load_yaml_data()
        if data is None:
            logger.warning("No se pudieron cargar los datos YAML. La base de datos no será poblada.")
            return

        try:
            # UDNs
            udns_data = data.get('UDNs', [])
            udns_map = {}
            logger.info(f"Procesando {len(udns_data)} UDNs...")
            for udn_data in udns_data:
                udn_name = udn_data['name']
                udn, created = UDN.objects.get_or_create(name=udn_name)
                udns_map[udn_name] = udn
            logger.info("UDNs procesadas correctamente")

            # Sectores
            sectors_data = data.get('Sectors', [])
            sectors_map = {}
            logger.info(f"Procesando {len(sectors_data)} Sectores...")
            for sector_data in sectors_data:
                sector_name = sector_data['name']
                sector, created = Sector.objects.get_or_create(name=sector_name)

                for udn_name in sector_data.get('udns', []):
                    try:
                        sector.udn.add(udns_map[udn_name])
                    except KeyError:
                        logger.warning(f"UDN '{udn_name}' no encontrado al agregar al sector '{sector_name}'")
                sectors_map[sector_name] = sector
            logger.info("Sectores procesados correctamente")

            # Categorías de Incidencias
            issue_categories_data = data.get('IssueCategories', [])
            issue_categories_map = {}
            logger.info(f"Procesando {len(issue_categories_data)} Categorías de Incidencias...")
            for category_data in issue_categories_data:
                category_name = category_data['name']
                issue_category, created = IssueCategory.objects.get_or_create(name=category_name)
                issue_categories_map[category_name] = issue_category

                for sector_name in category_data.get('sectors', []):
                    try:
                        issue_category.sector.add(sectors_map[sector_name])
                    except KeyError:
                        logger.warning(f"Sector '{sector_name}' no encontrado al agregar a la categoría '{category_name}'")
            logger.info("Categorías de Incidencias procesadas correctamente")

            # Incidencias
            issues_data = data.get('Issues', [])
            logger.info(f"Procesando {len(issues_data)} Incidencias...")
            issues_created = 0
            issues_errors = 0
            for issue_data in issues_data:
                issue_name = issue_data['name']
                issue_category_name = issue_data['issue_category']
                try:
                    issue_category = issue_categories_map[issue_category_name]
                    issue, created = Issue.objects.get_or_create(
                        issue_category=issue_category,
                        name=issue_name,
                        defaults={
                            'description': issue_data['description'],
                            'display_name': issue_data.get('display_name', issue_name)
                        }
                    )
                    issues_created += 1
                except KeyError:
                    logger.warning(f"Categoría '{issue_category_name}' no encontrada al crear incidencia '{issue_name}'")
                    issues_errors += 1
                except Exception as e:
                    logger.error(f"Error al crear incidencia '{issue_name}': {str(e)}")
                    issues_errors += 1
            
            logger.info(f"Incidencias procesadas: {issues_created} creadas, {issues_errors} errores")
            logger.info("Población de la base de datos completada.")
            
            # Crear los grupos de modelos después de que la base de datos esté poblada
            self.create_model_groups(sender, **kwargs)

        except Exception as e:
            logger.error(f"Error durante la población de la base de datos: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")

    def create_superuser(self, sender, **kwargs):
        from django.contrib.auth.models import User
        if User.objects.filter(username='admin').exists():
            logger.info('Superuser "admin" already exists.')
            return

        secret_key = os.environ.get('SECRET_KEY')
        if not secret_key:
            logger.error('SECRET_KEY environment variable not set.')
            return

        User.objects.create_superuser('admin', None, secret_key)
        logger.info('Superuser "admin" created successfully.')

    def create_model_groups(self, sender, **kwargs):
        from django.contrib.auth.models import Group
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        from .models import UDN, Sector

        data = self.load_yaml_data()
        if not data:
            logger.warning("No se pudieron cargar los datos YAML. No se crearán los grupos para los modelos.")
            return

        try:
            with transaction.atomic():
                # Crear grupos por defecto
                default_group_names = ["Operator", "Auditor", "Support", "Administrative"]
                default_groups = {}
                for group_name in default_group_names:
                    group, created = Group.objects.get_or_create(name=group_name)
                    default_groups[group_name] = group
                    logger.info("{} grupo por defecto: {}", "Creado" if created else "Existente", group_name)

                # Obtener tipos de contenido y permisos
                udn_content_type = ContentType.objects.get(app_label='core', model='udn')
                sector_content_type = ContentType.objects.get(app_label='core', model='sector')
                udn_view_permission = Permission.objects.get(codename='view_udn', content_type=udn_content_type)
                sector_view_permission = Permission.objects.get(codename='view_sector', content_type=sector_content_type)

                # Crear y asignar grupos para UDNs
                udns_data = data.get('UDNs', [])
                for udn_data in udns_data:
                    udn_name = udn_data['name']
                    group_name = f"UDN {udn_name}"
                    group, created = Group.objects.get_or_create(name=group_name)
                    group.permissions.add(udn_view_permission)
                    logger.info("Grupo creado/verificado: {}", group_name)
                    try:
                        udn_instance = UDN.objects.get(name=udn_name)
                        udn_instance.groups.add(group)
                        udn_instance.save()
                        logger.info("Grupo {} asignado a UDN: {}", group_name, udn_name)
                    except UDN.DoesNotExist:
                        logger.warning("UDN {} no encontrado al asignar el grupo {}", udn_name, group_name)

                # Crear y asignar grupos para Sectores
                sectors_data = data.get('Sectors', [])
                for sector_data in sectors_data:
                    sector_name = sector_data['name']
                    group_name = f"SECTOR {sector_name}"
                    group, created = Group.objects.get_or_create(name=group_name)
                    group.permissions.add(sector_view_permission)
                    logger.info("Grupo creado/verificado: {}", group_name)
                    try:
                        sector_instance = Sector.objects.get(name=sector_name)
                        sector_instance.groups.add(group)
                        sector_instance.save()
                        logger.info("Grupo {} asignado a Sector: {}", group_name, sector_name)
                    except Sector.DoesNotExist:
                        logger.warning("Sector {} no encontrado al asignar el grupo {}", sector_name, group_name)

                logger.info("Grupos por defecto y grupos para UDN y Sector creados/verificados exitosamente.")

        except Exception as e:
            logger.error("Error al crear los grupos para los modelos: {}", e)
            import traceback
            logger.error("Traceback: {}", traceback.format_exc())
