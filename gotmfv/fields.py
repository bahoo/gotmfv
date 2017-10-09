from django.forms import Textarea, TextInput
from .models import Precinct


class TextyForeignKey(TextInput):
    pass


class TextyManyToManySelect(Textarea):

    def format_value(self, value):
        if value:
            return '\n'.join(value)
        return value

    def value_from_datadict(self, data, files, name):
        default = super(TextyManyToManySelect, self).value_from_datadict(data, files, name)
        if "*" in default:
            return Precinct.objects.filter(name__contains=default.replace("*", ""))
        return Precinct.objects.filter(code__in=default.split("\r\n"))