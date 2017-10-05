from django import forms
from django.contrib.gis import admin
from superpack.admin.options import LayerMappingAdmin
from .fields import TextyManyToManySelect
from .models import Committee, Area, Precinct, Person


class AreaAdminForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = Area
        widgets = {
            'precincts': TextyManyToManySelect
        }


class AreaInlineAdmin(admin.StackedInline):
    model = Area
    form = AreaAdminForm


class CommitteeAdminForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = Committee
        widgets = {
            'precincts': TextyManyToManySelect
        }


@admin.register(Committee)
class CommitteeAdmin(admin.ModelAdmin):
    form = CommitteeAdminForm
    inlines = [AreaInlineAdmin]


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    form = AreaAdminForm


@admin.register(Precinct)
class PrecinctAdmin(LayerMappingAdmin):
    list_display = ['name', 'code']
    search_fields = ['name', 'code']

    def get_queryset(self, request):
        return super(PrecinctAdmin, self).get_queryset(request).defer('geom') 


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    pass


