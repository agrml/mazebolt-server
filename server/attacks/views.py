from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View

from server.attacks.controllers import (
    create_instances,
    delete_instances,
    run_attack,
    update_instance_ips,
)
from server.attacks.forms import AttackForm, InstanceFormSet, LaunchNewInstancesForm
from server.attacks.models import Attack


class InstanceListView(View):
    template = 'attacks/instances.html'

    def get(self, request):
        return render(
            request=request,
            template_name=self.template,
            context={
                'running_instances_formset': InstanceFormSet,
                'launch_new_instances_form': LaunchNewInstancesForm,
            }
        )

    def post(self, request):
        if 'instances_count' in request.POST:
            return self._create_instances(request)

        formset = InstanceFormSet(request.POST)
        if not formset.is_valid():
            # review: add better error handling for real world
            raise ValidationError(f'invalid form data: {formset.errors}')
        selected_instances = [
            data['id']
            for data in formset.cleaned_data
            if data['is_selected']
        ]

        if 'start_test_on_selected' in formset.data:
            selected_instance_ids = ','.join(str(instance.id) for instance in selected_instances)
            return HttpResponseRedirect(f'start-test?instance_ids={selected_instance_ids}')

        delete_instances(selected_instances)
        # review: it were better to show a success message and then refresh the page,
        # but we don't have time for implementing the frontend
        return render(
            request=request,
            template_name=self.template,
            context={
                'running_instances_formset': InstanceFormSet,
                'launch_new_instances_form': LaunchNewInstancesForm,
            }
        )

    def _create_instances(self, request):
        form = LaunchNewInstancesForm(request.POST)
        if not form.is_valid():
            # review: add better error handling for real world
            raise ValidationError('invalid form data')
        # review: If we had a better fronted, we would propagate errors into View's code
        # and show them. For MVP we only log them.
        create_instances(form.cleaned_data['instances_count'])
        return render(
            request=request,
            template_name=self.template,
            context={
                'running_instances_formset': InstanceFormSet,
                'launch_new_instances_form': LaunchNewInstancesForm,
            }
        )


class AttackStartView(View):
    template = 'attacks/start-attack.html'

    def get(self, request):
        preselected_instance_ids = request.GET.get('instance_ids')
        form = AttackForm
        if preselected_instance_ids:
            instance_ids = [int(id_) for id_ in preselected_instance_ids.split(',')]
            form = AttackForm(initial={'instances': instance_ids})
        return render(
            request=request,
            template_name=self.template,
            context={
                'start_new_attack_form': form,
            }
        )

    def post(self, request):
        form = AttackForm(request.POST)
        if not form.is_valid():
            # review: add better error handling for real world
            raise ValidationError('invalid form data')

        instances = form.cleaned_data['instances']
        for instance in instances:
            if not instance.ip:
                update_instance_ips()
                break
        # review: for real world we should check IPs again and implement error page,
        # but I dont have time for it

        attack = Attack.objects.create(
            name=form.cleaned_data['name'],
            sh_command=form.cleaned_data['sh_command'],
        )
        attack.instances.set(form.cleaned_data['instances'])
        run_attack(attack)
        return HttpResponseRedirect('tests')

