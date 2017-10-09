from django import forms
from .fields import TextyForeignKey, TextyManyToManySelect
from .models import Committee, Area, Precinct, Person


class AreaAdminForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = Area
        widgets = {
            'precincts': TextyManyToManySelect
        }


class CommitteeAdminForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = Committee
        widgets = {
            'precincts': TextyManyToManySelect
        }


class PersonAdminForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = Person
        widgets = {
            'precinct': TextyForeignKey
        }