from django import forms
from django.forms import modelformset_factory

from server.attacks.models import Attack, Instance


class InstanceForm(forms.ModelForm):

    is_selected = forms.BooleanField(required=False)
    name = forms.CharField(disabled=True)
    status = forms.CharField(disabled=True)
    ip = forms.CharField(disabled=True, required=False)
    # todo: created
    #  there's a problem to place read-only field in the form
    #  we may put it strictly inside html or search for a solution
    #  but again, it's not the main point of the exercise I hope

    class Meta:
        model = Instance
        fields = ('is_selected', 'name', 'status', 'ip')


InstanceFormSet = modelformset_factory(Instance, InstanceForm, extra=0)


class LaunchNewInstancesForm(forms.Form):

    instances_count = forms.IntegerField(max_value=1000, min_value=1)


class AttackForm(forms.ModelForm):

    instances = forms.ModelMultipleChoiceField(
        queryset=Instance.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Attack
        fields = ['name', 'instances', 'sh_command']
