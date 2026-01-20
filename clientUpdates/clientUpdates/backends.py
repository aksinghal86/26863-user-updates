from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from .models import pwsCreds
from django.contrib.auth.hashers import check_password

# class PwsTableAuthBackend(BaseBackend):
#     def authenticate(self, request, username=None, password=None, **kwargs):
#         try:
#             # Retrieve the user from the PWS table using form_userid and form_pw
#             pws_record = Pws.objects.get(form_userid=username)
#             print(password, pws_record.form_pw)
#             if pws_record and password == pws_record.form_pw:
#                 # Check if a User exists with the same username
#                 user, created = User.objects.get_or_create(username=username)
#                 if created:
#                     user.set_password(password)
#                     user.save()
#                 return user
#         except Pws.DoesNotExist:
#             return None
#
#     def get_user(self, user_id):
#         try:
#             return User.objects.get(pk=user_id)
#         except User.DoesNotExist:
#             return None


class pwsCredsAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Retrieve the user from the PWS table using form_userid and form_pw
            pws_record = pwsCreds.objects.get(username=username)
            if pws_record and password == pws_record.password:
                # Check if a User exists with the same username
                user, created = User.objects.get_or_create(username=username)
                if created:
                    user.set_password(password)
                    user.save()
                return user
        except pwsCreds.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None