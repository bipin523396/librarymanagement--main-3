"""
Create or reset delivery staff login (use on Render shell).

  python manage.py bootstrap_delivery --username ram --password ram123
"""

import os

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from pymongo import MongoClient

from bookhub_backend.mongo_config import get_mongodb_uri
from library.models import DeliveryStaff


class Command(BaseCommand):
    help = 'Create or update a delivery user + DeliveryStaff profile (MongoDB-safe).'

    def add_arguments(self, parser):
        parser.add_argument('--username', default='ram', help='Delivery login username')
        parser.add_argument('--password', default='ram123', help='Login password')
        parser.add_argument('--phone', default='9800000000', help='Phone number')
        parser.add_argument('--vehicle', default='DL-01', help='Vehicle number')

    def _sync_mongo_user(self, username, password):
        uri = get_mongodb_uri()
        if not uri:
            return
        db_name = os.getenv('MONGODB_NAME', 'bookhub_db')
        coll = MongoClient(uri)[db_name].auth_user
        hashed = make_password(password)
        coll.update_one(
            {'username': username},
            {
                '$set': {
                    'username': username,
                    'password': hashed,
                    'is_superuser': False,
                    'is_staff': True,
                    'is_active': True,
                },
            },
            upsert=True,
        )

    def handle(self, *args, **options):
        username = options['username'].strip()
        password = options['password']
        phone = options['phone']
        vehicle = options['vehicle']

        self._sync_mongo_user(username, password)

        uri = get_mongodb_uri()
        db_name = os.getenv('MONGODB_NAME', 'bookhub_db')
        db = MongoClient(uri)[db_name] if uri else None
        doc = db.auth_user.find_one({'username': username}) if db is not None else None
        mongo_id = str(doc['_id']) if doc and doc.get('_id') else None

        user = User.objects.filter(username=username).first()
        if user:
            user.set_password(password)
            user.is_staff = True
            user.is_active = True
            user.is_superuser = False
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Updated delivery user: {username} (id={user.pk})'))
        else:
            user = User.objects.create_user(username=username, password=password)
            user.is_staff = True
            user.is_active = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created delivery user: {username} (id={user.pk})'))

        staff = None
        created = False
        if mongo_id:
            try:
                from bson import ObjectId

                staff = DeliveryStaff.objects.filter(user_id__in=[mongo_id, ObjectId(mongo_id)]).first()
            except Exception:
                staff = DeliveryStaff.objects.filter(user_id=mongo_id).first()
        if staff is None and mongo_id:
            from bson import ObjectId

            db.library_deliverystaff.update_one(
                {'user_id': ObjectId(mongo_id)},
                {
                    '$set': {
                        'user_id': ObjectId(mongo_id),
                        'phone': phone,
                        'vehicle_number': vehicle,
                        'active': True,
                    },
                },
                upsert=True,
            )
            staff = DeliveryStaff.objects.filter(user_id__in=[mongo_id, ObjectId(mongo_id)]).first()
            created = staff is None
        elif staff is None:
            staff, created = DeliveryStaff.objects.get_or_create(
                user=user,
                defaults={
                    'phone': phone,
                    'vehicle_number': vehicle,
                    'active': True,
                },
            )
        else:
            created = False
        if staff is not None:
            staff.phone = phone
            staff.vehicle_number = vehicle
            staff.active = True
            try:
                staff.save()
            except Exception:
                if mongo_id:
                    from bson import ObjectId

                    db.library_deliverystaff.update_one(
                        {'user_id': ObjectId(mongo_id)},
                        {'$set': {'phone': phone, 'vehicle_number': vehicle, 'active': True}},
                    )
        uid = mongo_id or (getattr(staff, 'user_id', None) if staff else None)
        self.stdout.write(
            self.style.SUCCESS(
                f'{"Created" if created else "Updated"} DeliveryStaff for {username} (user_id={uid})'
            )
        )
        self.stdout.write(self.style.SUCCESS('Synced delivery user to MongoDB auth_user.'))
        self.stdout.write('Login at /en/library/login/ with this username and password.')
