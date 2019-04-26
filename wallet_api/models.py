# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django import forms
from django.contrib.gis.db import models

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
    name = models.CharField(primary_key=True, max_length=60)

    class Meta:
        managed = False
        db_table = 'towns'

    def __str__(self):
        return self.name



class District(models.Model):
    name = models.CharField(max_length=60)
    townname = models.ForeignKey(Town, models.DO_NOTHING, db_column='townname')

    class Meta:
        managed = False
        db_table = 'districts'

    def __str__(self):
        return "%s , %s" % (self.name , self.townname)



class Merchant(models.Model):
    lastname = models.CharField(max_length=60)
    firstname = models.CharField(max_length=60, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDERS, null=True)
    cninumber = models.CharField(max_length=10)
    cniexpirationdate = models.DateField()
    phonenumber = models.CharField(max_length=9)
    login = models.CharField(max_length=25)
    password = models.CharField(max_length=25)

    class Meta:
        managed = False
        db_table = 'merchants'

    def __str__(self):
        return "%s %s" % (self.lastname , self.firstname)



class MerchantPoint(models.Model):
    name = models.CharField(max_length=60, blank=True, null=True)
    area = models.CharField(max_length=200)
    position = models.PointField()
    isopen = models.BooleanField(blank=True, null=True)
    balance = models.DecimalField(max_digits=19, decimal_places=5, null=True)
    district = models.ForeignKey(District, models.DO_NOTHING, db_column='districtid')
    merchant = models.ForeignKey(Merchant, models.DO_NOTHING, db_column='merchantid')

    class Meta:
        managed = False
        db_table = 'merchant_points'

    def __str__(self):
        return "%s - %s" % (self.name, self.area)



class Customer(models.Model):
    phonenumber = models.CharField(primary_key=True, max_length=9)
    lastname = models.CharField(max_length=60)
    firstname = models.CharField(max_length=60, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDERS, null=True)
    cninumber = models.CharField(max_length=10)
    cniexpirationdate = models.DateField()
    secret = models.CharField(max_length=6)
    balance = models.DecimalField(max_digits=19, decimal_places=5, null=True)

    class Meta:
        managed = False
        db_table = 'customers'

    def __str__(self):
        return self.lastname



class Comment(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    title = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    customernumber = models.ForeignKey(Customer, models.DO_NOTHING, db_column='customernumber')
    merchantpoint = models.ForeignKey(MerchantPoint, models.DO_NOTHING, db_column='merchantpointid')

    class Meta:
        managed = False
        db_table = 'comments'



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
    date = models.DateTimeField(auto_now_add=True)
    type = models.TextField(choices=TRANSACTION_TYPES)
    isvalidated = models.BooleanField(default=False)
    expectedvalidationdate = models.DateField()
    validationdate = models.DateTimeField()
    beneficiarynumber = models.IntegerField(db_column='beneficiaryid')
    customernumber = models.ForeignKey(Customer, models.DO_NOTHING, db_column='customernumber')
    merchantpoint = models.ForeignKey(MerchantPoint, models.DO_NOTHING, db_column='merchantpointid')
    otp = models.ForeignKey(Otp, models.DO_NOTHING, db_column='otpcode')

    class Meta:
        managed = False
        db_table = 'transactions'



class WaitingLine(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    customernumber = models.ForeignKey(Customer, models.DO_NOTHING, db_column='customernumber')
    merchantpoint = models.ForeignKey(MerchantPoint, models.DO_NOTHING, db_column='merchantpointid')
    wasserved = models.BooleanField()
    servicedate = models.DateTimeField(null=True)

    class Meta:
        managed = False
        db_table = 'waiting_lines'