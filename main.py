import json, re
from os import getenv


def write_file(filename, dict_data):
    with open(filename, 'w') as f:
        json.dump(dict_data, f)


def read_file(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data


def get_urns_to_import(preview_new_state_file):
    urns = list()
    with open(preview_new_state_file, 'r') as f:
        response = json.load(f)
        for res in response["steps"]:
            if res["op"] == "create":
                urns.append(res["urn"])
    print(f"Found URNs (create): {len(urns)}")
    return urns


def change_urn_project_name(urn, new_project, old_project, to_old=False):
    if to_old:
        return urn.replace(f"::{new_project}::", f"::{old_project}::") 
    return urn.replace(f"::{old_project}::", f"::{new_project}::")


def filter_resources_by_urn(old_state_file, urns, new_project, old_project):
    resources = list()
    with open(old_state_file, 'r') as f:
        state = json.load(f)
        for sts in state["deployment"]["resources"]:
            # copying provider definition
            if sts["type"] == "pulumi:providers:aws":
                resources.append(sts)
            # copyng resources
            if change_urn_project_name(sts["urn"], new_project["name"], old_project["name"]) in urns:
                resources.append(sts)
    return resources


def append_resources_in_new_state(new_state_file, resources_to_import):
    new_state = read_file(new_state_file)
    for resource in resources_to_import:
        new_state["deployment"]["resources"].append(resource)
    write_file(f"to_import_{new_state_file}", new_state)


def replace_project_name(new_state_file, new_project, old_project):
    with open(f"to_import_{new_state_file}", "r") as f:
        data = f.read()
    data = data.replace(f"::{old_project['name']}::", f"::{new_project['name']}::")
    data = data.replace(f"::{old_project['name']}-{old_project['stack']}",
                        f"::{new_project['name']}-{new_project['stack']}")
    write_file(f"to_import_{new_state_file}", json.loads(data))


def write_state_delete(urns, new_project, old_project):
    script = "#! /bin/bash\n\n"

    for urn in urns:
        script += f"pulumi state delete -y " \
                  f"\"{change_urn_project_name(urn, new_project['name'], old_project['name'], to_old=True)}\"\n"
    
    with open("old_stack_delete_resouces_imported.sh", "w") as f:
        f.write(script)


def get_project_names(filename):
    data = read_file(filename)
    project = data["deployment"]["secrets_providers"]["state"]["project"]
    stack = data["deployment"]["secrets_providers"]["state"]["stack"]
    return {'name': project, 'stack': stack}


def main():
    print(f"Starting")
    new_state_file = getenv("NEW_STATE_FILE")
    preview_new_state_file = getenv("PREVIEW_NEW_STATE_FILE")
    old_state_file = getenv("OLD_STATE_FILE")
    old_project = get_project_names(old_state_file)
    new_project = get_project_names(new_state_file)
    print(f"New Project: {new_project}")
    print(f"Old/Current Project: {old_project}")

    urns = get_urns_to_import(preview_new_state_file)
    resources = filter_resources_by_urn(old_state_file, urns, new_project, old_project)
    append_resources_in_new_state(new_state_file, resources)
    replace_project_name(new_state_file, new_project, old_project)
    write_state_delete(urns, new_project, old_project)
    print(f'DONE!! Check the file: to_import_{new_state_file}')

main()
    
