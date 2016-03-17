import os.path
import datetime
import codecs
import sys
# Constants
# Could be translated to properties
__version = 1
__supported_state_versions = [1]
__supported_update_versions = [1]
__default_depth = 2
__force_depth = True
__cache_updates = False
__cache_state = False

#####################
# STATE PARSER
#################

def parse_raw_state(raw_state, time = 0, API_version = None, name='GitSpace'):
    print("Parsing State",file=sys.stderr)
    time = 0 # Override time argument to avoid lightning
    if __cache_state:
        with codecs.open("raw_state.py", "w+",'utf-8') as f:
            print("state=%s"%raw_state,file=f)
    if API_version == None:
        API_version = __version
    if API_version not in __supported_state_versions:
        raise Exception('Unknown API version: ' + API_version)
    if API_version == 1:
        if time != 0:
            time = parse_git_time_format(time)
        state = {}
        state['api version'] = 1
        state['real_time'] = False
        state['type'] = 'state'
        state['repo'] = name
        state['timestamp'] = time
        state['state'] = _extract_folders(raw_state['tree'],API_version,time)
    #   with open("state_output.txt","w+") as f:
    #       _write_readable_structure_to_file(f,state)
        if __force_depth:
            _apply_depth(state['state'])
        return state

def _extract_folders(tree, API_version,time):
    '''
    list tree: list of files/folders sorted hierical
    API version should already be checked'''
    if API_version == 1:
        folders = [] # Return argument
        folder_map = {} # Quick access to speed up child to parent object
        folder_map[None] = folders # Add root to list
        for node in tree:
            # Extract path, name and parent.
            # Root is None.
            path = os.path.dirname(node['path'])
            name = os.path.basename(node['path'])
            parent = folder_map[path] if len(path) > 0 else None
            if node['type'] in ['tree','commit']:
                _handle_tree_type(API_version,node,parent,name,folder_map,time)
            elif node['type'] == 'blob':
                # Files have type blob
                # A second pass is used to calculate file type ratio
                if parent != None: # Just skip root
                    _handle_blob_type(API_version,node,parent,folder_map)
            else:
                raise Exception("Unexpected git node type: " + node['type'])

        # Second pass to fix file extension ratios
        _fix_file_ratios(folders,API_version)
        return folders

def _fix_file_ratios(tree,API_version):
    '''Recursively divides all '''
    return
    if API_version == 1:
        for folder in tree:
            for ext in folder['filetypes']:
                if folder['size'] > 0:
                    # zero sized files have no impact
                    ext['part']/=folder['size']
            _fix_file_ratios(folder['subfolder'],API_version)

def _apply_depth(folders,depth= __default_depth):
    for f in folders:
        if depth <= 1:
            f['subfolder'] = []
            if 'action' in f:
                if f['action'] == 'none':
                    f['action'] = 'update'
        else:
            _apply_depth(f['subfolder'],depth-1)


def _handle_tree_type(API_version,node,parent,name,folder_map,time = 0):
    '''Creates a folder

       dict node: dictionary representing the file
       string path: the path to the file
       string name: the name of the file
       dict folder_map: dictionary {<foldername (string)> -> <folder dictionary>}
       returns: None'''
    if API_version == 1:
        # Folder base
        folder = _create_empty_state_folder(name,time)
        # Add new folder to folder map
        folder_map[node['path']] = folder

        if parent == None:
            # Special case for root folders.
            # Should be added directly to the root
            # instead of a parent dictionary.
            folder_map[parent].append(folder)
        else:
            #.append current folder to parent.
            # No needs for parent_exists checks
            # since inputed list is sorted hierarchical
            parent['subfolder'].append(folder)

def _create_empty_state_folder(name,date = 0):
    folder = {}
    folder['name'] = name
    folder['last modified date'] = date
    folder['last modified by'] = "none"
    folder['subfolder'] = []
    folder['filetypes'] = []
    return folder

def _handle_blob_type(API_version,node,parent,folder_map):
    '''Adds the size of the blob to the parent
       folder. Adds its extension to the parents
       extension list. The extension is added with
       actual size instead of ratio.

       dict node: dictionary representing the file
       string path: the path to the file
       dict folder_map: dictionary {<foldername (string)> -> <folder dictionary>}
       returns: None'''
    if API_version == 1:
        filename, ext = os.path.splitext(node['path'])
        # remove first dot, works with empty string
        ext = ext[1:]

        # Adds size to parent
        parent_ext = parent['filetypes']
        match = None
        # Find matching extension in parent
        for ext_dict in parent_ext:
            if ext_dict['extension'] == ext:
                match = ext_dict
                break
        # If no match, create new
        if not match:
            match = dict([('extension',ext),('part',0)])
            parent_ext.append(match)

        # Add new size to ratio
        match['part'] += node['size']





#####################
# UPDATE PARSER
#################





def parse_raw_updates(raw_updates, API_version = None,repo = "decentninja/GitSpace"):
    print("parsing %s commits"%len(raw_updates),file=sys.stderr)
    if __cache_updates:
        with codecs.open("raw_updates.py", "w+",'utf-8') as f:
            print("updates=%s"%raw_updates,file=f)
    if API_version == None:
        API_version = __version
    if API_version not in __supported_update_versions:
        raise Exception('Unknown API version: ' + API_version)
    if API_version == 1:
        parsed = [_parse_raw_update(update,API_version,repo=repo) for update in raw_updates]
        return parsed

def _parse_raw_update(raw_update, API_version, repo = "decentninja/GitSpace"):
    meta_info = raw_update
    date = meta_info['commit']['committer']['date']
    time = parse_git_time_format(date)
    meta_info['commit']['committer']['date'] = time

    changes = []
    change_map = {'': changes}

    update = {}
    update['type'] = 'update'
    update['repo'] = repo
    update['apiv'] = 1
    update['timestamp'] = time
    update['message'] = meta_info['commit']['message']
    update['direction'] = 'forward'
    update['override_filetypes'] = False
    update['forced'] = False # It WILL be with lower case, if written with json.dumps
    update['changes'] = changes
    update["check_threshold"] = False
    update['real_time'] = False
    for change in raw_update['files']:
        _parse_change(change,change_map,meta_info)
    if __force_depth:
         _apply_depth(update['changes'])

    return update


def _parse_change(change,change_map,meta_info):
    full = change['filename']
    path = os.path.dirname(full)
    name = os.path.basename(full)

    #Check if the parent subfolders exists
    if path not in change_map:
        parents = path.split('/')
        _create_subs('',parents,change_map,meta_info,change)


def _create_subs(parent,subs,change_map,meta_info,change):
    if len(subs) == 0: # Check end of recursion
        return
    #print("parent: ",parent," subs: ",subs)
    if parent not in change_map: # Check logic error
        raise Exception("Child before parent")

    # The current folder
    new_sub = "%s/%s"%(parent,subs[0]) if len(parent) > 0 else subs[0]
    if new_sub not in change_map: # If folder not seen before
        # Create folder
        current = _create_empty_change_subfolder(subs[0],meta_info)
        change_map[new_sub] = current # Add to list of folders

        action = change['status']
        if action in ['added','modified','changed']:
            current['action'] = 'update'
            if len(subs) == 1:
                filename, ext = os.path.splitext(change['filename'])
                match = None
                # Find matching extension in parent
                for ext_dict in current['filetypes']:
                    if ext_dict['extension'] == ext:
                        match = ext_dict
                        break
                # If no match, create new
                if not match:
                    match = dict([('extension',ext),('part',0)])
                    current['filetypes'].append(match)

                # Add new size to ratio
                match['part'] += change['additions']-change['deletions']

        elif action in ['removed']:
            if len(subs) == 1:
                current['action'] = 'delete'
        elif action in ['renamed']:
            #Only rename of files
            #Could possible be problem with folders
            current['action'] = 'update'
        else:
            raise Exception("ERROR: Unknown action: %s"%action)

        if parent == '': # Also make sure to add to root
            if current not in change_map[parent]:
                change_map[parent].append(current)
        else: # Add to parents subfolder
            change_map[parent]['subfolder'].append(current)

    # Create child folders of current folder
    _create_subs(new_sub,subs[1:],change_map,meta_info,change)

def _create_empty_change_subfolder(name,meta_info):
    change = {}
    change['name'] = name
    if not meta_info.get('author'):
        change['last modified by'] = "Unknown: %s"%meta_info['commit']['committer']['name']
    else:
        change['last modified by'] = meta_info['author']['login']
    change['action'] = "none"
    change['last modified date'] = meta_info['commit']['committer']['date']
    change['non_master_branch'] = False
    change['subfolder'] = []
    change['filetypes'] = []
    return change

def parse_git_time_format(date):
    return int(datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ").timestamp())

def create_user_states(state,users):
    print("Cloning State for %s users"%len(users),file=sys.stderr)
    return {user:_state_clone(state) for user in users}

def _state_clone(state):
    clone = {}
    clone['type'] = state['type']
    clone['repo'] = state['repo']
    clone['api version'] = state['api version']
    clone['timestamp'] = state['timestamp']
    clone["state"] = []
    clone['real_time'] = state['real_time']
    _recursive_state_clone(state['state'], clone['state'])
    return clone

def _recursive_state_clone(parent,c_parent):
    for sub in parent:
        c_sub = {}
        c_sub['last modified by'] = sub['last modified by']
        c_sub['last modified date'] = sub['last modified date']
        c_sub['name'] = sub['name']
        c_sub['subfolder'] = []
        c_sub['filetypes'] = [{k:v for k,v in a_type.items()} for a_type in sub['filetypes']]

        c_parent.append(c_sub)
        _recursive_state_clone(sub['subfolder'],c_sub['subfolder'])




#########
## STATE UPDATE
#######3

def update_state(state,updates):
    update_user_states({None:state},updates)

def update_user_states(user_states,updates):
    print("Applying %s updates to %s states"%(len(updates),len(user_states)),file=sys.stderr)
    for update in updates:
        _apply_update(user_states,update)

def _apply_update(user_states,update):
    fake_states = {user: {'subfolder':tree['state']} for user,tree in user_states.items()}
    fake_change = {'subfolder': update['changes']}
    for user,state in user_states.items():
        state['timestamp'] = update['timestamp']
    _update_children(fake_states,fake_change)

def _update_children(user_states,change):
    for sub in change['subfolder']:
        is_old_folder = any(s['name'] == sub['name'] for s in next(iter(user_states.values()))['subfolder'])

        # Add new folder to every tree
        # Only use the timestamp for None or correct user
        children = {}
        for user,user_sub in user_states.items():
            correct_user = sub['last modified by'] == user or user is None
            state_sub = None #Failsafe
            if not is_old_folder:
                new_folder = _create_empty_state_folder(sub['name'])
                user_sub['subfolder'].append(new_folder)
                state_sub = new_folder
            else:
                state_sub = next(usub for usub in user_sub['subfolder'] if usub['name']==sub['name'])

            children[user] = state_sub
            if sub['action'] == 'update':
                if correct_user:
                    state_sub['last modified date'] = sub['last modified date']
                    state_sub['last modified by'] = sub['last modified by']
                    for ext in sub['filetypes']:
                        match = None
                        # Find matching extension in parent
                        for ext_dict in state_sub['filetypes']:
                            if ext_dict['extension'] == ext['extension']:
                                match = ext_dict
                                break
                        # If no match, create new
                        if not match:
                            match = dict([('extension',ext['extension']),('part',0)])
                            state_sub['filetypes'].append(match)

                        # Add new size to ratio
                        match['part'] += ext['part']
            elif sub['action'] == 'delete':
                user_sub['subfolder'].remove(state_sub)
            elif sub['action'] == 'none':
                pass
            else:
                raise Exception('unknwown action: %s'%sub['action'])
        if not sub['action'] == 'delete':
            _update_children(children,sub)

def print_tree_structure(alist, keys = None):
    '''for manual debug'''
    def print_tree(depth,tree):
        for t in tree:
            print("\t"*depth,end='')
            for k,v in t.items():
                if keys == None or k in keys:
                    if k != 'subfolder':
                        print(k,v,end=', ')
            print()
            print_tree(depth+1,t["subfolder"])
    print_tree(0,alist)



######################
# PARSE HOOK DATA
######################
def hook_to_updates(hook):
    print("Parsing Hook",file=sys.stderr)
    commits = hook['commits'][::-1] #Reverse list
    return parse_raw_updates([_hook_commit_to_raw_update(c) for c in commits])

def _hook_commit_to_raw_update(hook):
    raw_update = {}

    # Change from format "2015-05-05T19:40:15-04:00"
    # To "2015-05-05T19:40:15Z"
    raw_update['commit'] = {}
    raw_update['commit']['committer'] = {}
    raw_update['commit']['committer']['date'] = hook['timestamp'][:19]+'Z'
    raw_update['commit']['message'] = hook['message']
    raw_update['commit']['committer']['name'] = hook['author']['name']
    raw_update['author'] = {}
    raw_update['author']['login'] = hook['author']['username']
    raw_update['files'] = []
    for action in ['added','removed','modified']:
        raw_update['files'] += [{'filename':f,'status':action,'additions':0,'deletions':0} for f in hook[action]]
    return raw_update


##################
# STATE TO UPDATE
##################

def state_to_update(state):
    print("Converting state to update",file=sys.stderr)
    update = {}
    update['type'] = "update"
    update['repo'] = state['repo']
    update['apiv'] = 1
    update['direction'] = "forward"
    update['override_filetypes'] = False
    update['forced'] = False
    update["changes"] = []
    update["timestamp"] = state["timestamp"]
    update["real_time"] = state["real_time"]
    update["check_threshold"] = True
    recursive_state_to_update(update['changes'], state['state'])
    return update

def recursive_state_to_update(parent,state):
    for sub in state:
        new_sub = {}
        new_sub['last modified by'] = sub['last modified by']
        new_sub['last modified date'] = sub['last modified date']
        new_sub['name'] = sub['name']
        new_sub['action'] = 'update'
        new_sub['subfolder'] = []
        new_sub['filetypes'] = [{k:v for k,v in a_type.items()} for a_type in sub['filetypes']]

        parent.append(new_sub)
        recursive_state_to_update(new_sub['subfolder'],sub['subfolder'])










#####################
# Davids hemliga hörna
#################

if __name__ == '__main__':
    from raw_state import state as rawstate
    from raw_updates import updates as rawupdates
    from hook import hook as hook
    hook_to_updates(hook)
    #print_tree_structure(hook_to_updates(hook)[0]['changes'])
