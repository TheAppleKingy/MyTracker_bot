from ...exc import RepositoryError


class TaskRepositoryError(RepositoryError):
    layer_instance_class_name = 'TaskRepository'


class UserRepositoryError(RepositoryError):
    layer_instance_class_name = 'UserRepository'


class GroupRepositoryError(RepositoryError):
    layer_instance_class_name = 'GroupRepository'
