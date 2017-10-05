from django.contrib.gis.db import models
from django.contrib.auth import get_user_model
from django.template.defaultfilters import slugify
from localflavor.us.models import PhoneNumberField


User = get_user_model()


STATUSES = (
        (None, '-'),
        ('email', 'Email'),
        ('voicemail', 'Voicemail'),
        ('will-walk', 'Will Walk'),
        ('picked-up-packet', 'Has Packet'),
        ('walked', 'Walked'),
        ('data-entered', 'Data Entered'),
        ('will-not-walk', 'Will Not Walk'),
    )



class Committee(models.Model):
    name = models.CharField(max_length=64)
    precincts = models.ManyToManyField('Precinct', blank=True)

    def __unicode__(self):
        return self.name


class Area(models.Model):
    name = models.CharField(max_length=64)
    committee = models.ForeignKey(Committee)
    precincts = models.ManyToManyField('Precinct', blank=True)
    point_person = models.ForeignKey(User, blank=True, null=True)

    def __unicode__(self):
        return self.name


class Precinct(models.Model):
    COUNTY_CODES = (('AD', "Adams"), ('AS', "Asotin"), ('BE', "Benton"), ('CH', "Chelan"), ('CM', "Clallam"), \
                    ('CR', "Clark"), ('CU', "Columbia"), ('CZ', "Cowlitz"), ('DG', "Douglas"), ('FE', "Ferry"), \
                    ('FR', "Franklin"), ('GA', "Garfield"), ('GR', "Grant"), ('GY', "Grays Harbor"), ('IS', "Island"), \
                    ('JE', "Jefferson"), ('KI', "King"), ('KP', "Kitsap"), ('KS', "Kittitas"), ('KT', "Klickitat"), \
                    ('LE', "Lewis"), ('LI', "Lincoln"), ('MA', "Mason"), ('OK', "Okanogan"), ('PA', "Pacific"), \
                    ('PE', "Pend Oreille"), ('PI', "Pierce"), ('SJ', "San Juan"), ('SK', "Skagit"), ('SM', "Skamania"), \
                    ('SN', "Snohomish"), ('SP', "Spokane"), ('ST', "Stevens"), ('TH', "Thurston"), ('WK', "Wahkiakum"), \
                    ('WL', "Walla Walla"), ('WM', "Whatcom"), ('WT', "Whitman"), ('XX', "Statewide"), ('YA', "Yakima"))
    name = models.CharField(max_length=32)
    code = models.CharField(max_length=4)
    county_code = models.CharField(max_length=2, choices=COUNTY_CODES)
    st_code = models.CharField(primary_key=True, max_length=12)
    geom = models.MultiPolygonField(blank=True, null=True, srid=4326)

    class Meta:
        unique_together = ('code', 'county_code')

    def __unicode__(self):
        return self.name


class Person(models.Model):
    full_name = models.CharField(max_length=255, null=True, blank=True)
    precinct = models.ForeignKey(Precinct, null=True, blank=True)
    email = models.EmailField(null=True, blank=True, max_length=128)
    phone_number = models.CharField(null=True, blank=True, max_length=128)
    pco = models.BooleanField(default=False)
    volunteer = models.BooleanField(default=False)
    delegate = models.BooleanField(default=False)
    status = models.CharField(default=None, choices=STATUSES, null=True, blank=True, max_length=32)
    notes = models.TextField(null=True, blank=True)
    mini_van = models.BooleanField(default=True, verbose_name='MiniVAN')

    def __unicode__(self):
        return self.full_name

    class Meta:
        ordering = ('precinct', 'status', 'full_name')