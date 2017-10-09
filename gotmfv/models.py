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
    people = models.ManyToManyField('Person', blank=True, related_name="committees")

    def __unicode__(self):
        return self.name


class Area(models.Model):
    name = models.CharField(max_length=64)
    committee = models.ForeignKey(Committee)
    precincts = models.ManyToManyField('Precinct', blank=True)
    point_person = models.ForeignKey(User, blank=True, null=True, related_name="area")

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(Area, self).save(*args, **kwargs)

        if self.template_emails.count() == 0:
            templates_to_create = [
                    {'person_status': None,
                    'subject': "%(first_name)s, can you help us get out the vote?",
                    'body': """Hi %%(first_name)s,

My name is %%(author_name)s, I'm a volunteer with the %(org_name)s.

Election Day is just around the corner, and we are excited to be ramping up our Get Out the Vote efforts. We are reaching out to %%(descriptor)s and wondered if you'd be interested in walking your precinct, %%(precinct_name)s? It would be a huge help toward turning out Democratic voters in your neighborhood, and with your help, we will win big on Election Day.

We have got a packet with a walk list and literature all ready to go. We can also set you up with a mobile phone app called MiniVAN, which makes walking your precinct a breeze.

Let me know if you're interested, and we'll get you all setup. We'd love to have your help in making this election a big success for Democrats.

Thanks, %%(first_name)s!

%%(author_name)s""" % {'org_name': self.committee.name}
                    },

                    {'person_status': "will-walk",
                    'subject': "%(first_name)s, your walk packet for %(precinct_name)s is ready for pickup",
                    'body': """Hi %(first_name)s,

Just a friendly heads up -- your precinct walk packet is available for pickup.



Please make a plan to scoop it up and walk your precinct (and let me know if you have any questions!)

Thanks!

%(author_name)s"""},

                    {
                    'person_status': "picked-up-packet",
                    'subject': "How's it going?",
                    'body': """Hey %(first_name)s,

Just checking in -- have you been able to walk your precinct?

Thanks!

%(author_name)s"""}]

            for tpl in templates_to_create:
                self.template_emails.create(**tpl)


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
    pco = models.BooleanField(verbose_name="PCO", default=False)
    volunteer = models.BooleanField(default=False)
    delegate = models.BooleanField(default=False)
    status = models.CharField(default=None, choices=STATUSES, null=True, blank=True, max_length=32)
    notes = models.TextField(null=True, blank=True)
    mini_van = models.BooleanField(default=True, verbose_name='MiniVAN')

    def __unicode__(self):
        return self.full_name

    class Meta:
        ordering = ('precinct', 'status', 'full_name')


class TemplateEmail(models.Model):
    person_status = models.CharField(default=None, choices=STATUSES, null=True, blank=True, max_length=32)
    subject = models.CharField(max_length=255, null=True, blank=True)
    body = models.TextField(blank=True, null=True)
    area = models.ForeignKey(Area, related_name="template_emails")