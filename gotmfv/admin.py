from django import forms
from django.contrib.gis import admin
from django.contrib.admin import SimpleListFilter
from django.db.models import Q
from django.utils.html import mark_safe
from superpack.admin.options import LayerMappingAdmin
from .admin_forms import AreaAdminForm, CommitteeAdminForm, PersonAdminForm
from .fields import TextyManyToManySelect
from .models import Area, Committee, Person, Precinct, TemplateEmail



class AreaInlineAdmin(admin.StackedInline):
    model = Area
    form = AreaAdminForm


class TemplateEmailInlineAdmin(admin.StackedInline):
    model = TemplateEmail


@admin.register(Committee)
class CommitteeAdmin(admin.ModelAdmin):
    form = CommitteeAdminForm
    inlines = [AreaInlineAdmin]


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    form = AreaAdminForm
    inlines = [TemplateEmailInlineAdmin]


@admin.register(Precinct)
class PrecinctAdmin(LayerMappingAdmin):
    list_display = ['name', 'code']
    search_fields = ['name', 'code']

    def get_queryset(self, request):
        return super(PrecinctAdmin, self).get_queryset(request).defer('geom') 


class AreaListFilter(SimpleListFilter):
    title = "Areas"
    parameter_name = "areas"

    def lookups(self, request, model_admin):
        # only one? skip it.
        if request.user.area.count() < 2:
            return ()
        return request.user.area.all().values_list('id', 'name')

    def queryset(self, request, queryset):
        if not request.GET.get('areas'):
            return queryset
        return queryset.filter(area_id__in=request.GET.get('areas').split(","))


class AffiliationListFilter(SimpleListFilter):
    title = "Affiliations"
    parameter_name = "affiliations"

    def lookups(self, request, model_admin):
        return (
                ('pco', 'PCO'),
                ('volunteer', 'Volunteer'),
                ('delegate', 'Delegate'),
            )

    def queryset(self, request, queryset):
        kwargs = {}
        if request.GET.get('affiliations'):
            kwargs[request.GET.get('affiliations')] = True
        return queryset.filter(**kwargs)


class PrecinctStatusListFilter(SimpleListFilter):
    title = "Precinct Status"
    parameter_name = 'precinct_status'

    def lookups(self, request, model_admin):
        return (
            ('needs-walker', "Needs Walker"),
            ('needs-packets', "Has Walker, Needs Packets"),
            ('needs-walk', "Has Packet, Needs to Walk"),
            ('needs-enter-data', "Has Walked, Needs to Enter Data"),
            ('done', "Done!")
        )

    def queryset(self, request, queryset):
        lookup_to_status = {
            'needs-walker': Q(Q(status='will-walk') | Q(status='picked-up-packet') | Q(status='walked') | Q(status='data-entered')),
            'needs-packets': {'status': 'will-walk'},
            'needs-walk': {'status': 'picked-up-packet'},
            'needs-enter-data': {'status': 'walked'},
            'done': {'status': 'data-entered'}
        }

        if self.value():

            if isinstance(lookup_to_status[self.value()], dict):
                matching = queryset.filter(**lookup_to_status[self.value()])
            elif isinstance(lookup_to_status[self.value()], list):
                matching = queryset.filter(*lookup_to_status[self.value()])
            else:
                matching = queryset.filter(lookup_to_status[self.value()])
            
            if self.value() == 'needs-walker':
                st_codes_to_exclude = matching.values_list('precinct', flat=True)
                return queryset.exclude(precinct__in=st_codes_to_exclude).exclude(status='will-not-walk')
            else:
                return matching

        return queryset


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    form = PersonAdminForm
    list_display = ['full_name', 'precinct', 'phone_number', 'linkable_email', 'status']
    list_filter = [AreaListFilter, 'status', PrecinctStatusListFilter, AffiliationListFilter]
    search_fields = ['full_name', 'email', 'phone_number', 'precinct__name']
    list_select_related = ['precinct']

    def linkable_email(self, obj):
        if not obj.email:
            return ''

        try:
            template = TemplateEmail.objects.get(area__committee__in=obj.committees.all(), person_status=obj.status)
        except TemplateEmail.DoesNotExist:
            # all good! Easy.
            return mark_safe("<a href=\"mailto:%(email)s\" target=\"_blank\">%(email)s</a>" % {'email': obj.email})

        if obj.pco:
            descriptor = "PCOs"
        elif obj.volunteer:
            descriptor = "volunteers"
        elif obj.delegate:
            descriptor = "precinct delegates"
        else:
            descriptor = "supporters"

        template_vars = {'first_name': obj.full_name.split(' ')[0],
                        'author_name': self.request.user.first_name,
                        'descriptor': descriptor,
                        'precinct_name': obj.precinct.name}

        params = {'subject': template.subject % template_vars,
                'body': "%0D%0A".join((template.body % template_vars).split('\n'))}

        return mark_safe("<a href=\"mailto:%(email)s%(params)s\" target=\"_blank\">%(email)s</a>" % {'email': obj.email, 'params': '?' +  "&".join(["=".join([k,v]) for k,v in params.iteritems()]) if params else ''})
    linkable_email.short_description = "Email"
    linkable_email.admin_order_field = "email"

    def get_queryset(self, request):
        self.request = request
        user_committees = request.user.area.all().values_list('committee_id', flat=True)
        return super(PersonAdmin, self).get_queryset(request).filter(committees__in=user_committees)