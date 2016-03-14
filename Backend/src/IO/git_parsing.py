import os.path
import datetime
import codecs
# Constants
# Could be translated to properties
__version = 1
__supported_state_versions = [1]
__supported_update_versions = [1]
__default_depth = 3
__force_depth = True
__cache_updates = False
__cache_state = False

#####################
# STATE PARSER
#################

def parse_raw_state(raw_state, time = 0, API_version = None):
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
		state['type'] = 'state'
		state['repo'] = 'GitSpace' # TODO placeholder
		state['state'] = _extract_folders(raw_state['tree'],API_version,time)
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
			if node['type'] == 'tree':
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
	folder['size'] = 0
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
	if __cache_updates:
		with codecs.open("raw_updates.py", "w+",'utf-8') as f:
			print("updates=%s"%raw_updates,file=f)
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
	time = parse_git_time_format(date)
	meta_info['committer']['date'] = time

	changes = []
	change_map = {'': changes}

	update = {}
	update['type'] = 'update'
	update['rep'] = 'GitSpace' # TODO placeholder
	update['apiv'] = 1
	update['message'] = meta_info['message']
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
		if action in ['added','modified']:
			current['action'] = 'update'
		elif action in ['removed']:
			if len(subs) == 0:
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
	change['size'] = 0
	change['user'] = meta_info['committer']['email']
	change['action'] = "none"
	change['timestamp'] = meta_info['committer']['date']
	change['non_master_branch'] = False
	change['subfolder'] = []
	change['filetypes'] = []
	return change

def parse_git_time_format(date):
	return int(datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ").timestamp())


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





#########
## STATE UPDATE
#######3




def update_state(state,updates):
	for update in updates:
		_apply_update(state,update)
	return state

def _apply_update(state,update):
	state_tree = state['state']

	fake_state = {'subfolder':state_tree}
	fake_change = {'subfolder': update['changes']}
	_update_children(fake_state,fake_change)

def _update_children(state,change):
	for sub in change['subfolder']:
		state_sub = None
		for s in state['subfolder']:
			if s['name'] == sub['name']:
				state_sub = s
				break
		if state_sub == None:
			new_folder = _create_empty_state_folder(sub['name'],sub['timestamp'])
			state['subfolder'].append(new_folder)
			state_sub = new_folder
		if sub['action'] in ['update','modified']:
			state_sub['last modified date'] = sub['timestamp']
			state_sub['last modified by'] = sub['user']
		elif sub['action'] == 'delete':
			change['subfolder'].remove(sub)
			return
		elif sub['action'] == 'none':
			pass
		else:
			raise Exception('unknwown action: %s'%sub['action'])
		if state_sub == None:
			raise Exception("Did not find sub in state: %s"%sub['name'])
		_update_children(state_sub,sub)

def print_tree_structure(alist):
	'''for manual debug'''
	def print_tree(depth,tree):
		for t in tree:
			if 'action' in t:
				print("  "*depth+t['name'],t['action'])
			else:
				print("  "*depth+t['name'],t['last modified date'],t['last modified by'])
			print_tree(depth+1,t["subfolder"])
	print_tree(0,alist)

#####################
# Davids hemliga hörna
#################

if __name__ == '__main__':
	from raw_state import state as rawstate
	from raw_updates import updates as rawupdates
	state = parse_raw_state(rawstate,time = "2016-02-23T19:30:35Z")
	updates = parse_raw_updates(rawupdates)
	print("BEFORE")
	print_tree_structure(state['state'])
	for u in updates:
		print(u['message'])
		print_tree_structure(u['changes'])
		update_state(state,[u])
		print("AFTER")
		print_tree_structure(state['state'])