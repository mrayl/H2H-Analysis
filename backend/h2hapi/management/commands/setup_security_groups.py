from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from h2hapi.models import Player

class Command(BaseCommand):
    help = 'Creates default security groups: Admin, AppUser, and Public'

    def handle(self, *args, **kwargs):
        # Super User Group
        admin_group, created = Group.objects.get_or_create(name='Administrators')
        if created:
            # Admins get all permissions on Player model
            ct = ContentType.objects.get_for_model(Player)
            permissions = Permission.objects.filter(content_type=ct)
            admin_group.permissions.set(permissions)
            self.stdout.write(self.style.SUCCESS("Created 'Administrators' group."))
        else:
            self.stdout.write("Group 'Administrators' already exists.")

        # App User
        app_user_group, created = Group.objects.get_or_create(name='AppUsers')
        if created:
            # App Users can View players (standard usage permissions)
            ct = ContentType.objects.get_for_model(Player)
            view_perm = Permission.objects.get(content_type=ct, codename='view_player')
            app_user_group.permissions.add(view_perm)
            self.stdout.write(self.style.SUCCESS("Created 'AppUsers' group."))
        else:
            self.stdout.write("Group 'AppUsers' already exists.")

        # Public
        anon_group, created = Group.objects.get_or_create(name='Public')
        if created:
            # Public can only View players
            ct = ContentType.objects.get_for_model(Player)
            view_perm = Permission.objects.get(content_type=ct, codename='view_player')
            anon_group.permissions.add(view_perm)
            self.stdout.write(self.style.SUCCESS("Created 'Public' group."))
        else:
            self.stdout.write("Group 'Public' already exists.")