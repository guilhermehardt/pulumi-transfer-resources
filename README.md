## Pulumi Transfer Resources

This script was created to help you move resouces from one project to another project stack, without recreating the resources on Pulumi.
The project idea is move resources exporting and importing the JSON state file.

- **new_state.json**: new stack status file;
- **preview_new_state.json**: preview state file (resources to be move);
- **old_state.json**: current/old stack (resouces moved from);

First, the resources inside preview_new_state.json are searched into old_state.json. The matched resources will be appended on new_state.json and the script will generate a final file **to_import_new_file.json**. This file should be used to import the resources into the new stack.

This project doesn`t make changes in Pulumi directly

### Steps
Creating the new stack:
```bash
$ pulumi stack init guilhermehardt/infrastructure/old_stack
$ pulumi up
$ pulumi stack export --file "new_state.json"
```
After move your projec to the new directory containing only the resources that you need move, it`s necessary run the pulumi preview commmand and save the output in json file:
```bash
$ pulumi preview --json > "preview_new_state.json"
```
Now we need to export the current/old stack state file:
```bash
$ pulumi stack export --file "old_state.json"
```
Copy the three files (new_state.json, preview_new_state.json and old_state.json) to this directory.     
Now we can create the python virtual env and run the script
```bash
$ python3 -m venv venv
$ source venv/bin/activate
$ export NEW_STATE_FILE="new_state.json"
$ export PREVIEW_NEW_STATE_FILE="preview_new_state.json"
$ export OLD_STATE_FILE="old_state.json"
$ python main.py
```
It`s possible to format json file 
```bash
$ cat <<< $(jq '.' to_import_${NEW_STATE_FILE}) > to_import_${NEW_STATE_FILE}
```
Now we need to use the file created by script to import the resouces into new stack:
```bash
$ export NEW_STATE_FILE="new_state.json"
$ pulumi stack import --file to_import_${NEW_STATE_FILE}
$ pulumi preview
```
At the end, the state of resources moved should be removed in old stack, to avoid duplication: 
**!!!** Before run the below shell script check if all resources was moved from old to new stack
```bash
$ bash ./old_state_delete_resouces_imported.sh
```
