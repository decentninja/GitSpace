import os.path
import datetime
# Constants
# Could be translated to properties
__version = 1
__supported_state_versions = [1]
__supported_update_versions = [1]
__default_depth = 4
__force_depth = True

#####################
# STATE PARSER
#################

def parse_raw_state(raw_state, API_version = None):
	with open("raw_state.txt","w+") as f:
		print(raw_state,file=f)
	if API_version == None:
		API_version = __version
	if API_version not in __supported_state_versions:
		raise Exception('Unknown API version: ' + API_version)
	if API_version == 1:
		state = {}
		state['api version'] = 1
		state['type'] = 'state'
		state['repo'] = 'PLACEHOLDER' # TODO placeholder
		state['timestamp'] = 52341414 # TODO placeholder
		state['state'] = _extract_folders(raw_state['tree'],API_version)
	#	with open("state_output.txt","w+") as f:
	#		_write_readable_structure_to_file(f,state)
		if __force_depth:
			_apply_depth(state['state'])
		return state

def _write_readable_structure_to_file(f,parsed_state):
	'''for manual debug'''
	def print_tree(depth,tree):
		for t in tree:
			print("  "*depth+t['name'],t['size'],t['filetypes'],file=f)
			print_tree(depth+1,t["subfolder"])
	print_tree(0,parsed_state['state'])

def _extract_folders(tree, API_version):
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
			if node['type'] == 'tree':
				_handle_tree_type(API_version,node,parent,name,folder_map)			
			elif node['type'] == 'blob':
				# Files have type blob
				# A second pass is used to calculate file type ratio
				_handle_blob_type(API_version,node,parent,folder_map)
			else:
				raise Exception("Unexpected git node type: " + node['type'])

		# Second pass to fix file extension ratios
		_fix_file_ratios(folders,API_version)
		return folders

def _fix_file_ratios(tree,API_version):
	'''Recursively divides all '''
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
					f['action'] = 'modified'
		else:
			_apply_depth(f['subfolder'],depth-1)


def _handle_tree_type(API_version,node,parent,name,folder_map):
	'''Creates a folder

	   dict node: dictionary representing the file
	   string path: the path to the file
	   string name: the name of the file
	   dict folder_map: dictionary {<foldername (string)> -> <folder dictionary>}
	   returns: None'''
	if API_version == 1:
		# Folder base
		folder = {}
		folder['name'] = name
		folder['size'] = 0
		folder['subfolder'] = []
		folder['filetypes'] = []

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
		parent['size'] += node['size']

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

def parse_raw_updates(raw_updates, API_version = None):
	with open("raw_updates.py","w+") as f:
		print("updates = " +str(raw_updates),file=f)
	if API_version == None:
		API_version = __version
	if API_version not in __supported_update_versions:
		raise Exception('Unknown API version: ' + API_version)
	if API_version == 1:
		parsed = [_parse_raw_update(update,API_version) for update in raw_updates]
		#write_updates_readable(parsed)
		return parsed

def _parse_raw_update(raw_update, API_version):
	meta_info = raw_update['commit']
	date = meta_info['committer']['date']
	time = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ").timestamp()

	changes = []
	change_map = {'': changes}

	update = {}
	update['type'] = 'update'
	update['rep'] = 'GitSpace' # TODO placeholder
	update['apiv'] = 1
	update['timestamp'] = time
	update['direction'] = 'forward'
	update['forced'] = False # will not be lower case when written :S
	update['changes'] = changes
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
		_create_subs('',parents,change_map,meta_info)
	diff = change_map[path]
	diff['action'] = change['status']


def _create_subs(parent,subs,change_map,meta_info):
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
		if parent == '': # Also make sure to add to root
			if current not in change_map[parent]:
				change_map[parent].append(current)
		else: # Add to parents subfolder
			change_map[parent]['subfolder'].append(current)
			
	# Create child folders of current folder
	child = _create_subs(new_sub,subs[1:],change_map,meta_info)

def _create_empty_change_subfolder(name,meta_info):
	change = {}
	change['name'] = name
	change['size'] = 0
	change['user'] = meta_info['committer']['name']
	change['action'] = "none"
	change['non_master_branch'] = False
	change['subfolder'] = []
	change['filetypes'] = []
	return change


def write_updates_readable(changes):
	def print_tree(depth,tree, fil):
		for t in tree:
			print("  "*depth,t['name'],"(",t['action'],",",t['user'],")",file=fil)
			print_tree(depth+1,t["subfolder"],fil)
	with open("changes.txt","w+") as f:
		for change in changes:
			print("\n\n-----------------------------------",file=f)
			print('timestamp: ',datetime.datetime.fromtimestamp(int(change['timestamp'])).strftime('%Y-%m-%d %H:%M:%S'),file=f)
			print_tree(0,change['changes'],f)



#####################
# Davids hemliga hörna
#################

if __name__ == '__main__':
	from raw_updates import update
	changes = parse_raw_updates(update)
	write_updates_readable(changes)