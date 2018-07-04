from typing import Type, List, Dict

from dero.manager.main import PipelineManager


def get_dict_of_pipeline_manager_names_and_instances_from_globals() -> Dict[str, PipelineManager]:
    managers = _get_objs_of_class_from_globals(PipelineManager)
    out_dict = {}
    for manager in managers:
        name = manager.name
        if name in out_dict:
            # Two cases where name may already be in dict. User has defined two pipeline managers with the same name,
            # or the same pipeline manager has been assigned to another variable.

            # Here the same pipeline manager has been assigned to multiple variables. Just skip adding this time
            if manager is out_dict[name]:
                continue

            # Here this is actually a different pipeline manager than the one stored. They both have the same name,
            # so this must be a user error of defining multiple pipeline managers without different names
            raise ValueError(
                f'found multiple PipelineManager objects with the name {name}, cannot determine which to select')
        out_dict[name] = manager

    return out_dict


def _get_objs_of_class_from_globals(klass: Type) -> List:
    selected_items = []
    for variable_name, value in globals().items():
        if isinstance(value, klass):
            selected_items.append(value)

    return selected_items


def _get_dicts_of_variable_name_value_from_globals_by_class(klass: Type) -> Dict[str, any]:
    selected_dict = {}
    for variable_name, value in globals().items():
        if isinstance(value, klass):
            if variable_name in selected_dict:
                raise ValueError(
                    f'found multiple {klass} objects assigned to {variable_name}, cannot determine which to select')
            selected_dict[variable_name] = value

    return selected_dict