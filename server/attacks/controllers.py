import threading
import logging
import uuid

import requests
from requests import RequestException

from server.attacks.models import Attack, Instance
from server.clients.google_cloud import (
    delete_instance as delete_instance_google_cloud,
    create_instance as create_instance_google_cloud,
    list_instances,
    base_image_name,
)

logger = logging.getLogger(__name__)


def delete_instance(instance_name: str):
    try:
        delete_instance_google_cloud(instance_name)
    except Exception:
        logger.exception(
            'Could not delete instance %s', instance_name
        )
        return

    instance = Instance.objects.get(name=instance_name)
    instance.status = Instance.StatusChoices.TERMINATED
    instance.save()
    instance.attacks_history.update(status=Attack.StatusChoices.FINISHED)


def delete_instances(instances: list[Instance]):
    # review: in production we would limit number of parallel requests,
    # so google cloud's rate limited had not affected us
    delete_tasks = [
        threading.Thread(target=delete_instance, args=(instance.name,))
        for instance in instances
    ]
    for thread in delete_tasks:
        thread.start()

    # review: we might not wait for threads to finish
    # if we implemented page updates and deletion success checking in the frontend
    for thread in delete_tasks:
        thread.join()


def send_command(instance, attack):
    try:
        response = requests.post(
            url=f'http://{instance.ip}:8000/task',
            json={
                'sh_command': attack.sh_command,
            },
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            }
        )
    except RequestException:
        logger.exception('Could not run a task on instance %s: %s')
        return

    if response.status_code != 200:
        logger.error(
            'Could not run a task on instance %s: %s. ret code: %s',
            instance.id, instance.name, response.status_code,
        )
        return

    instance.status = Instance.StatusChoices.RUNNING_TEST
    instance.save()
    instance.attacks_history.add(attack)


def run_attack(attack: Attack):
    threads = [
        threading.Thread(target=send_command, args=(instance, attack))
        for instance in attack.instances.all()
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    attack.status = Attack.StatusChoices.RUNNING
    attack.save()


def create_instance():
    instance_name = 'mbexam-' + str(uuid.uuid4())
    try:
        create_instance_google_cloud(
            instance_name=instance_name,
            image_name=base_image_name,
            size='n1-highcpu-2',
        )
    except Exception:
        logger.exception('Could not create an instance')
        return

    Instance.objects.create(name=instance_name)


def create_instances(instance_count: int):
    # review: we would do retries in production
    threads = [
        threading.Thread(target=create_instance)
        for i in range(instance_count)
    ]
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


def update_instance_ips():
    # review: we update ips for all instances for almost no additional cost. good enough for MVP.
    db_instances = Instance.objects.all()
    db_instance_by_name = {
        instance.name: instance
        for instance in db_instances
    }
    instance_dicts = list_instances()
    for instance_dict in instance_dicts:
        ip = instance_dict['networkInterfaces'][0]['accessConfigs'][0].get('natIP')
        if not ip:
            logger.warning('An instance without connectivity options found')
            continue
        name = instance_dict['name']
        db_instance = db_instance_by_name.get(name)
        if db_instance:
            db_instance.ip = ip
    Instance.objects.bulk_update(db_instances, ['ip'])


def stop_tests():
    # todo
    raise NotImplementedError()
