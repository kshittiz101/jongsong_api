from ..models import Designation


def default_designation_instance():
    return Designation.objects.get(name="Other")
