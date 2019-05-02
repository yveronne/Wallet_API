# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django import forms
from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.contrib import admin

LOG_ACTIONS = (
    ("Connexion", "Connexion"),
    ("Déconnexion", "Déconnexion"),
    ("Ouverture", "Ouverture"),
    ("Fermeture", "Fermeture")
)
TRANSACTION_TYPES = (
    ("Dépôt", "Dépôt"),
    ("Retrait", "Retrait"),
    ("Paiement", "Paiement")
)
GENDERS = (
    ('M', 'Masculin'),
    ('F', 'Féminin')
)


class Town(models.Model):
    name = models.CharField(primary_key=True, max_length=60, verbose_name='Nom')

    class Meta:
        managed = False
        db_table = 'towns'
        verbose_name = 'Ville'
        verbose_name_plural = 'Villes'

    def __str__(self):
        return self.name



class District(models.Model):
    name = models.CharField(max_length=60, verbose_name='Nom du quartier')
    townname = models.ForeignKey(Town, models.DO_NOTHING, db_column='townname', verbose_name='Ville')

    class Meta:
        managed = False
        db_table = 'districts'
        verbose_name = 'Quartier'
        verbose_name_plural = 'Quartiers'

    def __str__(self):
        return "%s , %s" % (self.name , self.townname)


class Merchant(models.Model):
    lastname = models.CharField(max_length=60, verbose_name='Nom')
    firstname = models.CharField(max_length=60, blank=True, null=True, verbose_name='Prénom')
    gender = models.CharField(max_length=1, choices=GENDERS, null=True, verbose_name='Genre')
    cninumber = models.CharField(max_length=10, verbose_name='Numéro de CNI')
    cniexpirationdate = models.DateField(verbose_name='Date d\'expiration de la CNI')
    phonenumber = models.CharField(max_length=9, verbose_name='Numéro de téléphone')
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING, db_column='userid', verbose_name='Utilisateur')

    class Meta:
        managed = False
        db_table = 'merchants'
        verbose_name = 'Marchand'
        verbose_name_plural = 'Marchands'

    def __str__(self):
        return "%s %s" % (self.lastname , self.firstname)



class MerchantPoint(models.Model):
    name = models.CharField(max_length=60, blank=True, null=True, verbose_name='Nom')
    area = models.CharField(max_length=200, verbose_name='Secteur')
    position = models.PointField(verbose_name='Position géographique')
    isopen = models.BooleanField(blank=True, null=True, verbose_name='Est ouvert?')
    balance = models.DecimalField(max_digits=19, decimal_places=5, null=True, verbose_name='Solde')
    district = models.ForeignKey(District, models.DO_NOTHING, db_column='districtid', verbose_name='Quartier')
    merchant = models.ForeignKey(Merchant, models.DO_NOTHING, db_column='merchantid', verbose_name='Marchand')

    class Meta:
        managed = False
        db_table = 'merchant_points'
        verbose_name = 'Point marchand'
        verbose_name_plural = 'Points marchands'

    def __str__(self):
        return "%s - %s" % (self.name, self.area)



class Customer(models.Model):
    phonenumber = models.CharField(primary_key=True, max_length=9, verbose_name='Numéro de téléphone')
    lastname = models.CharField(max_length=60, verbose_name='Nom')
    firstname = models.CharField(max_length=60, blank=True, null=True, verbose_name='Prénom')
    gender = models.CharField(max_length=1, choices=GENDERS, null=True, verbose_name='Genre')
    cninumber = models.CharField(max_length=10, verbose_name='Numéro de CNI')
    cniexpirationdate = models.DateField(verbose_name='Date d\'expiration de la CNI')
    secret = models.CharField(max_length=6, verbose_name='Code secret')
    balance = models.DecimalField(max_digits=19, decimal_places=5, null=True, verbose_name='Solde')

    class Meta:
        managed = False
        db_table = 'customers'
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'

    def __str__(self):
        return "%s - %s" % (self.lastname, self.phonenumber)

    def full_name(self):
        return "%s %s" % (self.lastname, self.firstname)



class Comment(models.Model):
    date = models.DateTimeField(auto_now_add=True, verbose_name='Date')
    title = models.TextField(blank=True, null=True, verbose_name='Titre')
    content = models.TextField(blank=True, null=True, verbose_name='Contenu')
    customernumber = models.ForeignKey(Customer, models.DO_NOTHING, db_column='customernumber', verbose_name='Numéro de téléphone du client')
    merchantpoint = models.ForeignKey(MerchantPoint, models.DO_NOTHING, db_column='merchantpointid', verbose_name='Point marchand')

    class Meta:
        managed = False
        db_table = 'comments'
        verbose_name = 'Commentaire'
        verbose_name_plural = 'Commentaires'

    def __str__(self):
        return "%s - %s" % (self.title, self.customernumber)



class ConnectionLog(models.Model):
    merchantpointid = models.IntegerField()
    action = models.TextField(choices=LOG_ACTIONS)
    date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'connection_logs'



class Otp(models.Model):
    code = models.CharField(primary_key=True, max_length=7)
    expirationdate = models.DateTimeField()
    wasverified = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'otp'


class Transaction(models.Model):
    date = models.DateTimeField(auto_now_add=True, verbose_name='Date')
    type = models.TextField(choices=TRANSACTION_TYPES, verbose_name='Type')
    isvalidated = models.BooleanField(default=False, verbose_name='A été validée?')
    expectedvalidationdate = models.DateField(verbose_name='Date de validation attendue')
    validationdate = models.DateTimeField(verbose_name='Date effective de validation')
    beneficiarynumber = models.IntegerField(db_column='beneficiaryid', verbose_name='Bénéficiaire')
    customernumber = models.ForeignKey(Customer, models.DO_NOTHING, db_column='customernumber', verbose_name='Client')
    merchantpoint = models.ForeignKey(MerchantPoint, models.DO_NOTHING, db_column='merchantpointid', verbose_name='Point marchand')
    otp = models.ForeignKey(Otp, models.DO_NOTHING, db_column='otpcode')

    class Meta:
        managed = False
        db_table = 'transactions'
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'

    def __str__(self):
        return "%s_%s_%s" %(self.date, self.type, self.customernumber)



class WaitingLine(models.Model):
    date = models.DateTimeField(auto_now_add=True, verbose_name='Date')
    customernumber = models.ForeignKey(Customer, models.DO_NOTHING, db_column='customernumber', verbose_name='Numéro de téléphone du client')
    merchantpoint = models.ForeignKey(MerchantPoint, models.DO_NOTHING, db_column='merchantpointid', verbose_name='Point marchand')
    wasserved = models.BooleanField(verbose_name='A été servi ?')
    servicedate = models.DateTimeField(null=True, verbose_name='Date de service')

    class Meta:
        managed = False
        db_table = 'waiting_lines'
        verbose_name = 'File d\'attente'
        verbose_name_plural = 'Files d\'attente'


# class CustomerForm(ModelForm):
#     class Meta:
#         model = Customer
#         fields = ['firstname', 'lastname']

