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
	if API_version == None:
		API_version = __version
	if API_version not in __supported_state_versions:
		raise Exception('Unknown API version: ' + API_version)
	if API_version == 1:
		state = {}
		state['api version'] = 1
		state['type'] = 'state'
		state['repo'] = 'GitSpace' # TODO placeholder
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
		folder = _create_empty_state_folder(name)
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
		_create_subs('',parents,change_map,meta_info)
	if path != '':
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
	change['timestamp'] = meta_info['committer']['date']
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
		if sub['action'] == 'modified':
			state_sub['last modified date'] = sub['timestamp']
			state_sub['last modified by'] = sub['user']
		elif sub['action'] == 'delete':
			change['subfolder'].remove(sub)
			return
		elif sub['action'] == 'added':
			new_folder = _create_empty_state_folder(sub['name'],sub['timestamp'])
			state['subfolder'].append(new_folder)
			state_sub = new_folder
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
	state = {'timestamp': 52341414, 'api version': 1, 'type': 'state', 'repo': 'GitSpace', 'state': [{'filetypes': [], 'last modified date': 0, 'subfolder': [{'filetypes': [{'extension': 'py', 'part': 0}], 'last modified date': 0, 'subfolder': [], 'name': 'Test', 'size': 0, 'last modified by': 'none'}, {'filetypes': [{'extension': 'py', 'part': 1.0}], 'last modified date': 0, 'subfolder': [{'filetypes': [{'extension': 'py', 'part': 1.0}], 'last modified date': 0, 'subfolder': [], 'name': 'IO', 'size': 11334, 'last modified by': 'none'}], 'name': 'src', 'size': 2360, 'last modified by': 'none'}], 'name': 'Backend', 'size': 0, 'last modified by': 'none'}, {'filetypes': [{'extension': '', 'part': 0.05538904208128522}, {'extension': 'md', 'part': 0.07577029133197459}, {'extension': 'json', 'part': 0.10094712864164969}, {'extension': 'xml', 'part': 0.5829037285697158}, {'extension': 'js', 'part': 0.16580745713943174}, {'extension': 'project', 'part': 0.01918235223594293}], 'last modified date': 0, 'subfolder': [{'filetypes': [{'extension': 'md', 'part': 1.0}], 'last modified date': 0, 'subfolder': [{'filetypes': [{'extension': 'js', 'part': 1.0}], 'last modified date': 0, 'subfolder': [], 'name': 'after_prepare', 'size': 2735, 'last modified by': 'none'}], 'name': 'hooks', 'size': 3018, 'last modified by': 'none'}, {'filetypes': [{'extension': 'png', 'part': 1.0}], 'last modified date': 0, 'subfolder': [], 'name': 'resources', 'size': 123067, 'last modified by': 'none'}, {'filetypes': [{'extension': 'scss', 'part': 1.0}], 'last modified date': 0, 'subfolder': [{'filetypes': [{'extension': 'scss', 'part': 1.0}], 'last modified date': 0, 'subfolder': [], 'name': 'components', 'size': 1773, 'last modified by': 'none'}], 'name': 'scss', 'size': 854, 'last modified by': 'none'}, {'filetypes': [{'extension': 'html', 'part': 1.0}], 'last modified date': 0, 'subfolder': [{'filetypes': [{'extension': 'css', 'part': 1.0}], 'last modified date': 0, 'subfolder': [], 'name': 'css', 'size': 448666, 'last modified by': 'none'}, {'filetypes': [{'extension': 'png', 'part': 1.0}], 'last modified date': 0, 'subfolder': [], 'name': 'img', 'size': 4757, 'last modified by': 'none'}, {'filetypes': [{'extension': 'js', 'part': 1.0}], 'last modified date': 0, 'subfolder': [], 'name': 'js', 'size': 29042, 'last modified by': 'none'}, {'filetypes': [{'extension': 'html', 'part': 1.0}], 'last modified date': 0, 'subfolder': [], 'name': 'views', 'size': 2728, 'last modified by': 'none'}], 'name': 'www', 'size': 878, 'last modified by': 'none'}], 'name': 'ControlPanel', 'size': 8341, 'last modified by': 'none'}, {'filetypes': [{'extension': '', 'part': 1.0}], 'last modified date': 0, 'subfolder': [{'filetypes': [{'extension': 'meta', 'part': 1.0}], 'last modified date': 0, 'subfolder': [{'filetypes': [{'extension': 'cs', 'part': 0.8793548387096775}, {'extension': 'meta', 'part': 0.12064516129032259}], 'last modified date': 0, 'subfolder': [{'filetypes': [{'extension': 'cs', 'part': 0.9594312362315108}, {'extension': 'meta', 'part': 0.04056876376848911}], 'last modified date': 0, 'subfolder': [], 'name': 'ImageEffects', 'size': 69906, 'last modified by': 'none'}], 'name': 'Editor', 'size': 1550, 'last modified by': 'none'}, {'filetypes': [{'extension': '', 'part': 0.0}, {'extension': 'mat', 'part': 0.9179114799446749}, {'extension': 'meta', 'part': 0.06224066390041494}, {'extension': 'physicMaterial', 'part': 0.019847856154910096}], 'last modified date': 0, 'subfolder': [], 'name': 'Materials', 'size': 14460, 'last modified by': 'none'}, {'filetypes': [{'extension': 'prefab', 'part': 0.96987087517934}, {'extension': 'meta', 'part': 0.03012912482065997}], 'last modified date': 0, 'subfolder': [], 'name': 'Prefabs', 'size': 41820, 'last modified by': 'none'}, {'filetypes': [{'extension': 'meta', 'part': 0.003574406345479778}, {'extension': 'fbx', 'part': 0.02349933901252311}, {'extension': 'jpg', 'part': 0.9729262546419971}], 'last modified date': 0, 'subfolder': [{'filetypes': [{'extension': 'mat', 'part': 0.9444444444444444}, {'extension': 'meta', 'part': 0.05555555555555555}], 'last modified date': 0, 'subfolder': [], 'name': 'Materials', 'size': 12960, 'last modified by': 'none'}, {'filetypes': [{'extension': 'meta', 'part': 1.0}], 'last modified date': 0, 'subfolder': [], 'name': 'fonts', 'size': 192, 'last modified by': 'none'}], 'name': 'Resources', 'size': 1458424, 'last modified by': 'none'}, {'filetypes': [{'extension': '', 'part': 0.0}, {'extension': 'unity', 'part': 0.9860364913027289}, {'extension': 'meta', 'part': 0.013963508697271131}], 'last modified date': 0, 'subfolder': [], 'name': 'Scenes', 'size': 37598, 'last modified by': 'none'}, {'filetypes': [{'extension': '', 'part': 0.0}, {'extension': 'cs', 'part': 0.266614199641332}, {'extension': 'meta', 'part': 0.03318324323626934}, {'extension': 'dll', 'part': 0.7002025571223986}], 'last modified date': 0, 'subfolder': [], 'name': 'Scripts', 'size': 77509, 'last modified by': 'none'}, {'filetypes': [{'extension': 'meta', 'part': 1.0}], 'last modified date': 0, 'subfolder': [{'filetypes': [{'extension': 'meta', 'part': 1.0}], 'last modified date': 0, 'subfolder': [], 'name': 'Effects', 'size': 889, 'last modified by': 'none'}], 'name': 'Standard Assets', 'size': 127, 'last modified by': 'none'}, {'filetypes': [{'extension': 'meta', 'part': 0.02515496612368459}, {'extension': 'zip', 'part': 0.10227764163182933}, {'extension': 'txt', 'part': 0.8725673922444861}], 'last modified date': 0, 'subfolder': [{'filetypes': [{'extension': 'meta', 'part': 0.7559241706161137}, {'extension': 'cs', 'part': 0.24407582938388625}], 'last modified date': 0, 'subfolder': [], 'name': 'Demo', 'size': 844, 'last modified by': 'none'}, {'filetypes': [{'extension': 'cs', 'part': 0.9982833232001717}, {'extension': 'meta', 'part': 0.0017166767998283324}], 'last modified date': 0, 'subfolder': [], 'name': 'Editor', 'size': 139805, 'last modified by': 'none'}, {'filetypes': [{'extension': 'png', 'part': 0.2279802160088826}, {'extension': 'meta', 'part': 0.04166750782275159}, {'extension': 'guiskin', 'part': 0.7303522761683658}], 'last modified date': 0, 'subfolder': [], 'name': 'Skin', 'size': 99070, 'last modified by': 'none'}], 'name': 'UniMerge', 'size': 27748, 'last modified by': 'none'}], 'name': 'Assets', 'size': 1536, 'last modified by': 'none'}, {'filetypes': [{'extension': 'asset', 'part': 0.9981825172136591}, {'extension': 'txt', 'part': 0.0018174827863409178}], 'last modified date': 0, 'subfolder': [], 'name': 'ProjectSettings', 'size': 28611, 'last modified by': 'none'}], 'name': 'MainScreen', 'size': 370, 'last modified by': 'none'}]}
	updates = [{'forced': False, 'type': 'update', 'message': 'Some tweeking. Needs a lot more work but we should wait for folder depth', 'rep': 'GitSpace', 'changes': [{'action': 'none', 'name': 'MainScreen', 'filetypes': [], 'timestamp': 1456924922.0, 'subfolder': [{'action': 'none', 'name': 'Assets', 'filetypes': [], 'timestamp': 1456924922.0, 'subfolder': [{'action': 'modified', 'name': 'Materials', 'filetypes': [], 'timestamp': 1456924922.0, 'subfolder': [], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}, {'action': 'modified', 'name': 'Prefabs', 'filetypes': [], 'timestamp': 1456924922.0, 'subfolder': [], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}, {'action': 'modified', 'name': 'Scenes', 'filetypes': [], 'timestamp': 1456924922.0, 'subfolder': [], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}], 'apiv': 1, 'direction': 'forward'}, {'forced': False, 'type': 'update', 'message': 'More small tweeks', 'rep': 'GitSpace', 'changes': [{'action': 'none', 'name': 'MainScreen', 'filetypes': [], 'timestamp': 1456925628.0, 'subfolder': [{'action': 'none', 'name': 'Assets', 'filetypes': [], 'timestamp': 1456925628.0, 'subfolder': [{'action': 'modified', 'name': 'Materials', 'filetypes': [], 'timestamp': 1456925628.0, 'subfolder': [], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}, {'action': 'modified', 'name': 'Scenes', 'filetypes': [], 'timestamp': 1456925628.0, 'subfolder': [], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}, {'action': 'modified', 'name': 'ProjectSettings', 'filetypes': [], 'timestamp': 1456925628.0, 'subfolder': [], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}], 'apiv': 1, 'direction': 'forward'}, {'forced': False, 'type': 'update', 'message': 'Large improvement to line rendering', 'rep': 'GitSpace', 'changes': [{'action': 'none', 'name': 'MainScreen', 'filetypes': [], 'timestamp': 1456930277.0, 'subfolder': [{'action': 'none', 'name': 'Assets', 'filetypes': [], 'timestamp': 1456930277.0, 'subfolder': [{'action': 'modified', 'name': 'Materials', 'filetypes': [], 'timestamp': 1456930277.0, 'subfolder': [], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}, {'action': 'modified', 'name': 'Prefabs', 'filetypes': [], 'timestamp': 1456930277.0, 'subfolder': [], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}, {'action': 'modified', 'name': 'Scenes', 'filetypes': [], 'timestamp': 1456930277.0, 'subfolder': [], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}, {'action': 'modified', 'name': 'Scripts', 'filetypes': [], 'timestamp': 1456930277.0, 'subfolder': [], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}, {'action': 'modified', 'name': 'ProjectSettings', 'filetypes': [], 'timestamp': 1456930277.0, 'subfolder': [], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}], 'apiv': 1, 'direction': 'forward'}, {'forced': False, 'type': 'update', 'message': 'Small bloom changes', 'rep': 'GitSpace', 'changes': [{'action': 'none', 'name': 'MainScreen', 'filetypes': [], 'timestamp': 1456933855.0, 'subfolder': [{'action': 'none', 'name': 'Assets', 'filetypes': [], 'timestamp': 1456933855.0, 'subfolder': [{'action': 'modified', 'name': 'Materials', 'filetypes': [], 'timestamp': 1456933855.0, 'subfolder': [], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}, {'action': 'modified', 'name': 'Prefabs', 'filetypes': [], 'timestamp': 1456933855.0, 'subfolder': [], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}, {'action': 'modified', 'name': 'Scenes', 'filetypes': [], 'timestamp': 1456933855.0, 'subfolder': [], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}, {'action': 'modified', 'name': 'ProjectSettings', 'filetypes': [], 'timestamp': 1456933855.0, 'subfolder': [], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}], 'apiv': 1, 'direction': 'forward'}, {'forced': False, 'type': 'update', 'message': 'Update cueing and timestamp updates', 'rep': 'GitSpace', 'changes': [{'action': 'none', 'name': 'MainScreen', 'filetypes': [], 'timestamp': 1456936590.0, 'subfolder': [{'action': 'none', 'name': 'Assets', 'filetypes': [], 'timestamp': 1456936590.0, 'subfolder': [{'action': 'modified', 'name': 'Prefabs', 'filetypes': [], 'timestamp': 1456936590.0, 'subfolder': [], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}, {'action': 'modified', 'name': 'Scenes', 'filetypes': [], 'timestamp': 1456936590.0, 'subfolder': [], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}, {'action': 'modified', 'name': 'Scripts', 'filetypes': [], 'timestamp': 1456936590.0, 'subfolder': [], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}], 'apiv': 1, 'direction': 'forward'}, {'forced': False, 'type': 'update', 'message': 'Websocket mock working + cleaned data', 'rep': 'GitSpace', 'changes': [{'action': 'modified', 'name': 'ControlPanel', 'filetypes': [], 'timestamp': 1457002241.0, 'subfolder': [{'action': 'none', 'name': 'scss', 'filetypes': [], 'timestamp': 1457002241.0, 'subfolder': [{'action': 'modified', 'name': 'components', 'filetypes': [], 'timestamp': 1457002241.0, 'subfolder': [], 'user': 'Victor Larsson', 'non_master_branch': False, 'size': 0}], 'user': 'Victor Larsson', 'non_master_branch': False, 'size': 0}, {'action': 'modified', 'name': 'www', 'filetypes': [], 'timestamp': 1457002241.0, 'subfolder': [{'action': 'modified', 'name': 'js', 'filetypes': [], 'timestamp': 1457002241.0, 'subfolder': [], 'user': 'Victor Larsson', 'non_master_branch': False, 'size': 0}, {'action': 'modified', 'name': 'views', 'filetypes': [], 'timestamp': 1457002241.0, 'subfolder': [], 'user': 'Victor Larsson', 'non_master_branch': False, 'size': 0}], 'user': 'Victor Larsson', 'non_master_branch': False, 'size': 0}], 'user': 'Victor Larsson', 'non_master_branch': False, 'size': 0}], 'apiv': 1, 'direction': 'forward'}, {'forced': False, 'type': 'update', 'message': 'first prototype for update parsing\n\nSigned-off-by: Zercha <david.maskoo@gmail.com>', 'rep': 'GitSpace', 'changes': [{'action': 'none', 'name': 'Backend', 'filetypes': [], 'timestamp': 1457009830.0, 'subfolder': [{'action': 'none', 'name': 'src', 'filetypes': [], 'timestamp': 1457009830.0, 'subfolder': [{'action': 'modified', 'name': 'IO', 'filetypes': [], 'timestamp': 1457009830.0, 'subfolder': [], 'user': 'Zercha', 'non_master_branch': False, 'size': 0}], 'user': 'Zercha', 'non_master_branch': False, 'size': 0}], 'user': 'Zercha', 'non_master_branch': False, 'size': 0}], 'apiv': 1, 'direction': 'forward'}, {'forced': False, 'type': 'update', 'message': 'update parsing works\n\nSigned-off-by: Zercha <david.maskoo@gmail.com>', 'rep': 'GitSpace', 'changes': [{'action': 'none', 'name': 'Backend', 'filetypes': [], 'timestamp': 1457012381.0, 'subfolder': [{'action': 'none', 'name': 'src', 'filetypes': [], 'timestamp': 1457012381.0, 'subfolder': [{'action': 'modified', 'name': 'IO', 'filetypes': [], 'timestamp': 1457012381.0, 'subfolder': [], 'user': 'Zercha', 'non_master_branch': False, 'size': 0}], 'user': 'Zercha', 'non_master_branch': False, 'size': 0}], 'user': 'Zercha', 'non_master_branch': False, 'size': 0}], 'apiv': 1, 'direction': 'forward'}, {'forced': False, 'type': 'update', 'message': 'Tonemaping and other camera tweeks', 'rep': 'GitSpace', 'changes': [{'action': 'none', 'name': 'MainScreen', 'filetypes': [], 'timestamp': 1457012572.0, 'subfolder': [{'action': 'none', 'name': 'Assets', 'filetypes': [], 'timestamp': 1457012572.0, 'subfolder': [{'action': 'modified', 'name': 'Prefabs', 'filetypes': [], 'timestamp': 1457012572.0, 'subfolder': [], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}, {'action': 'modified', 'name': 'Scenes', 'filetypes': [], 'timestamp': 1457012572.0, 'subfolder': [], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}], 'apiv': 1, 'direction': 'forward'}, {'forced': False, 'type': 'update', 'message': 'Folder labels', 'rep': 'GitSpace', 'changes': [{'action': 'none', 'name': 'MainScreen', 'filetypes': [], 'timestamp': 1457015268.0, 'subfolder': [{'action': 'none', 'name': 'Assets', 'filetypes': [], 'timestamp': 1457015268.0, 'subfolder': [{'action': 'modified', 'name': 'Prefabs', 'filetypes': [], 'timestamp': 1457015268.0, 'subfolder': [], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}, {'action': 'modified', 'name': 'Scenes', 'filetypes': [], 'timestamp': 1457015268.0, 'subfolder': [], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}, {'action': 'modified', 'name': 'Scripts', 'filetypes': [], 'timestamp': 1457015268.0, 'subfolder': [], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}], 'apiv': 1, 'direction': 'forward'}, {'forced': False, 'type': 'update', 'message': 'added depth and updates\n\nSigned-off-by: Zercha <david.maskoo@gmail.com>', 'rep': 'GitSpace', 'changes': [{'action': 'none', 'name': 'Backend', 'filetypes': [], 'timestamp': 1457015860.0, 'subfolder': [{'action': 'none', 'name': 'src', 'filetypes': [], 'timestamp': 1457015860.0, 'subfolder': [{'action': 'modified', 'name': 'IO', 'filetypes': [], 'timestamp': 1457015860.0, 'subfolder': [], 'user': 'Zercha', 'non_master_branch': False, 'size': 0}], 'user': 'Zercha', 'non_master_branch': False, 'size': 0}], 'user': 'Zercha', 'non_master_branch': False, 'size': 0}], 'apiv': 1, 'direction': 'forward'}, {'forced': False, 'type': 'update', 'message': "Merge branch 'master' of https://github.com/decentninja/GitSpace", 'rep': 'GitSpace', 'changes': [{'action': 'none', 'name': 'MainScreen', 'filetypes': [], 'timestamp': 1457015869.0, 'subfolder': [{'action': 'none', 'name': 'Assets', 'filetypes': [], 'timestamp': 1457015869.0, 'subfolder': [{'action': 'modified', 'name': 'Prefabs', 'filetypes': [], 'timestamp': 1457015869.0, 'subfolder': [], 'user': 'Zercha', 'non_master_branch': False, 'size': 0}, {'action': 'modified', 'name': 'Scenes', 'filetypes': [], 'timestamp': 1457015869.0, 'subfolder': [], 'user': 'Zercha', 'non_master_branch': False, 'size': 0}, {'action': 'modified', 'name': 'Scripts', 'filetypes': [], 'timestamp': 1457015869.0, 'subfolder': [], 'user': 'Zercha', 'non_master_branch': False, 'size': 0}], 'user': 'Zercha', 'non_master_branch': False, 'size': 0}], 'user': 'Zercha', 'non_master_branch': False, 'size': 0}], 'apiv': 1, 'direction': 'forward'}, {'forced': False, 'type': 'update', 'message': 'fixed placeholder\n\nSigned-off-by: Zercha <david.maskoo@gmail.com>', 'rep': 'GitSpace', 'changes': [], 'apiv': 1, 'direction': 'forward'}, {'forced': False, 'type': 'update', 'message': 'Wow that speed', 'rep': 'GitSpace', 'changes': [{'action': 'none', 'name': 'MainScreen', 'filetypes': [], 'timestamp': 1457017499.0, 'subfolder': [{'action': 'none', 'name': 'Assets', 'filetypes': [], 'timestamp': 1457017499.0, 'subfolder': [{'action': 'modified', 'name': 'Prefabs', 'filetypes': [], 'timestamp': 1457017499.0, 'subfolder': [], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}, {'action': 'modified', 'name': 'Scenes', 'filetypes': [], 'timestamp': 1457017499.0, 'subfolder': [], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}, {'action': 'modified', 'name': 'ProjectSettings', 'filetypes': [], 'timestamp': 1457017499.0, 'subfolder': [], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}], 'apiv': 1, 'direction': 'forward'}, {'forced': False, 'type': 'update', 'message': 'fixed bug caused by root cahnges in updates\n\nSigned-off-by: Zercha <david.maskoo@gmail.com>', 'rep': 'GitSpace', 'changes': [{'action': 'none', 'name': 'Backend', 'filetypes': [], 'timestamp': 1457104097.0, 'subfolder': [{'action': 'none', 'name': 'src', 'filetypes': [], 'timestamp': 1457104097.0, 'subfolder': [{'action': 'modified', 'name': 'IO', 'filetypes': [], 'timestamp': 1457104097.0, 'subfolder': [], 'user': 'Zercha', 'non_master_branch': False, 'size': 0}], 'user': 'Zercha', 'non_master_branch': False, 'size': 0}], 'user': 'Zercha', 'non_master_branch': False, 'size': 0}], 'apiv': 1, 'direction': 'forward'}, {'forced': False, 'type': 'update', 'message': "Merge branch 'master' of https://github.com/decentninja/GitSpace", 'rep': 'GitSpace', 'changes': [{'action': 'none', 'name': 'MainScreen', 'filetypes': [], 'timestamp': 1457104104.0, 'subfolder': [{'action': 'none', 'name': 'Assets', 'filetypes': [], 'timestamp': 1457104104.0, 'subfolder': [{'action': 'modified', 'name': 'Prefabs', 'filetypes': [], 'timestamp': 1457104104.0, 'subfolder': [], 'user': 'Zercha', 'non_master_branch': False, 'size': 0}, {'action': 'modified', 'name': 'Scenes', 'filetypes': [], 'timestamp': 1457104104.0, 'subfolder': [], 'user': 'Zercha', 'non_master_branch': False, 'size': 0}], 'user': 'Zercha', 'non_master_branch': False, 'size': 0}, {'action': 'modified', 'name': 'ProjectSettings', 'filetypes': [], 'timestamp': 1457104104.0, 'subfolder': [], 'user': 'Zercha', 'non_master_branch': False, 'size': 0}], 'user': 'Zercha', 'non_master_branch': False, 'size': 0}], 'apiv': 1, 'direction': 'forward'}, {'forced': False, 'type': 'update', 'message': 'removed debugg output in parser\n\nSigned-off-by: Zercha <david.maskoo@gmail.com>', 'rep': 'GitSpace', 'changes': [{'action': 'none', 'name': 'Backend', 'filetypes': [], 'timestamp': 1457104170.0, 'subfolder': [{'action': 'none', 'name': 'src', 'filetypes': [], 'timestamp': 1457104170.0, 'subfolder': [{'action': 'modified', 'name': 'IO', 'filetypes': [], 'timestamp': 1457104170.0, 'subfolder': [], 'user': 'Zercha', 'non_master_branch': False, 'size': 0}], 'user': 'Zercha', 'non_master_branch': False, 'size': 0}], 'user': 'Zercha', 'non_master_branch': False, 'size': 0}], 'apiv': 1, 'direction': 'forward'}, {'forced': False, 'type': 'update', 'message': 'TCP Server for frontend, needs to integrate with new parser.', 'rep': 'GitSpace', 'changes': [{'action': 'none', 'name': 'Backend', 'filetypes': [], 'timestamp': 1457106234.0, 'subfolder': [{'action': 'modified', 'name': 'src', 'filetypes': [], 'timestamp': 1457106234.0, 'subfolder': [{'action': 'modified', 'name': 'IO', 'filetypes': [], 'timestamp': 1457106234.0, 'subfolder': [], 'user': 'Powiepon', 'non_master_branch': False, 'size': 0}], 'user': 'Powiepon', 'non_master_branch': False, 'size': 0}], 'user': 'Powiepon', 'non_master_branch': False, 'size': 0}], 'apiv': 1, 'direction': 'forward'}, {'forced': False, 'type': 'update', 'message': 'Cleaned code & structure + websocket communication', 'rep': 'GitSpace', 'changes': [{'action': 'none', 'name': 'ControlPanel', 'filetypes': [], 'timestamp': 1457273435.0, 'subfolder': [{'action': 'modified', 'name': 'www', 'filetypes': [], 'timestamp': 1457273435.0, 'subfolder': [{'action': 'added', 'name': 'js', 'filetypes': [], 'timestamp': 1457273435.0, 'subfolder': [], 'user': 'Victor Larsson', 'non_master_branch': False, 'size': 0}, {'action': 'modified', 'name': 'views', 'filetypes': [], 'timestamp': 1457273435.0, 'subfolder': [], 'user': 'Victor Larsson', 'non_master_branch': False, 'size': 0}], 'user': 'Victor Larsson', 'non_master_branch': False, 'size': 0}], 'user': 'Victor Larsson', 'non_master_branch': False, 'size': 0}], 'apiv': 1, 'direction': 'forward'}, {'forced': False, 'type': 'update', 'message': 'RepositoryScriptChange+Prepfab', 'rep': 'GitSpace', 'changes': [{'action': 'none', 'name': 'MainScreen', 'filetypes': [], 'timestamp': 1457295424.0, 'subfolder': [{'action': 'none', 'name': 'Assets', 'filetypes': [], 'timestamp': 1457295424.0, 'subfolder': [{'action': 'added', 'name': 'Prefabs', 'filetypes': [], 'timestamp': 1457295424.0, 'subfolder': [], 'user': 'adhag', 'non_master_branch': False, 'size': 0}, {'action': 'modified', 'name': 'Scripts', 'filetypes': [], 'timestamp': 1457295424.0, 'subfolder': [], 'user': 'adhag', 'non_master_branch': False, 'size': 0}], 'user': 'adhag', 'non_master_branch': False, 'size': 0}], 'user': 'adhag', 'non_master_branch': False, 'size': 0}], 'apiv': 1, 'direction': 'forward'}, {'forced': False, 'type': 'update', 'message': 'v2', 'rep': 'GitSpace', 'changes': [{'action': 'none', 'name': 'MainScreen', 'filetypes': [], 'timestamp': 1457295790.0, 'subfolder': [{'action': 'none', 'name': 'Assets', 'filetypes': [], 'timestamp': 1457295790.0, 'subfolder': [{'action': 'modified', 'name': 'Scripts', 'filetypes': [], 'timestamp': 1457295790.0, 'subfolder': [], 'user': 'adhag', 'non_master_branch': False, 'size': 0}], 'user': 'adhag', 'non_master_branch': False, 'size': 0}], 'user': 'adhag', 'non_master_branch': False, 'size': 0}], 'apiv': 1, 'direction': 'forward'}, {'forced': False, 'type': 'update', 'message': 'RepositoryPrefap_slightchange', 'rep': 'GitSpace', 'changes': [{'action': 'none', 'name': 'MainScreen', 'filetypes': [], 'timestamp': 1457296090.0, 'subfolder': [{'action': 'none', 'name': 'Assets', 'filetypes': [], 'timestamp': 1457296090.0, 'subfolder': [{'action': 'modified', 'name': 'Prefabs', 'filetypes': [], 'timestamp': 1457296090.0, 'subfolder': [], 'user': 'adhag', 'non_master_branch': False, 'size': 0}], 'user': 'adhag', 'non_master_branch': False, 'size': 0}, {'action': 'modified', 'name': 'ProjectSettings', 'filetypes': [], 'timestamp': 1457296090.0, 'subfolder': [], 'user': 'adhag', 'non_master_branch': False, 'size': 0}], 'user': 'adhag', 'non_master_branch': False, 'size': 0}], 'apiv': 1, 'direction': 'forward'}, {'forced': False, 'type': 'update', 'message': 'Changed color picking method\n\nOnly uses colors between red -> white and white -> blue now', 'rep': 'GitSpace', 'changes': [{'action': 'none', 'name': 'MainScreen', 'filetypes': [], 'timestamp': 1457297198.0, 'subfolder': [{'action': 'none', 'name': 'Assets', 'filetypes': [], 'timestamp': 1457297198.0, 'subfolder': [{'action': 'modified', 'name': 'Scripts', 'filetypes': [], 'timestamp': 1457297198.0, 'subfolder': [], 'user': 'Jonathan Golan', 'non_master_branch': False, 'size': 0}], 'user': 'Jonathan Golan', 'non_master_branch': False, 'size': 0}, {'action': 'modified', 'name': 'ProjectSettings', 'filetypes': [], 'timestamp': 1457297198.0, 'subfolder': [], 'user': 'Jonathan Golan', 'non_master_branch': False, 'size': 0}], 'user': 'Jonathan Golan', 'non_master_branch': False, 'size': 0}], 'apiv': 1, 'direction': 'forward'}, {'forced': False, 'type': 'update', 'message': "Handle Update Function\n\nAdding and updating should work (Haven't had test data to run with).\nDelete started but not yet done.", 'rep': 'GitSpace', 'changes': [{'action': 'none', 'name': 'MainScreen', 'filetypes': [], 'timestamp': 1457298484.0, 'subfolder': [{'action': 'none', 'name': 'Assets', 'filetypes': [], 'timestamp': 1457298484.0, 'subfolder': [{'action': 'modified', 'name': 'Scripts', 'filetypes': [], 'timestamp': 1457298484.0, 'subfolder': [], 'user': 'matlon', 'non_master_branch': False, 'size': 0}], 'user': 'matlon', 'non_master_branch': False, 'size': 0}], 'user': 'matlon', 'non_master_branch': False, 'size': 0}], 'apiv': 1, 'direction': 'forward'}, {'forced': False, 'type': 'update', 'message': 'Non animated camera', 'rep': 'GitSpace', 'changes': [{'action': 'none', 'name': 'MainScreen', 'filetypes': [], 'timestamp': 1457442549.0, 'subfolder': [{'action': 'none', 'name': 'Assets', 'filetypes': [], 'timestamp': 1457442549.0, 'subfolder': [{'action': 'modified', 'name': 'Scenes', 'filetypes': [], 'timestamp': 1457442549.0, 'subfolder': [], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}, {'action': 'modified', 'name': 'Scripts', 'filetypes': [], 'timestamp': 1457442549.0, 'subfolder': [], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}, {'action': 'modified', 'name': 'ProjectSettings', 'filetypes': [], 'timestamp': 1457442549.0, 'subfolder': [], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}], 'apiv': 1, 'direction': 'forward'}, {'forced': False, 'type': 'update', 'message': 'Star removal animation, no camera lerping yet...', 'rep': 'GitSpace', 'changes': [{'action': 'none', 'name': 'MainScreen', 'filetypes': [], 'timestamp': 1457446336.0, 'subfolder': [{'action': 'none', 'name': 'Assets', 'filetypes': [], 'timestamp': 1457446336.0, 'subfolder': [{'action': 'modified', 'name': 'Scenes', 'filetypes': [], 'timestamp': 1457446336.0, 'subfolder': [], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}, {'action': 'modified', 'name': 'Scripts', 'filetypes': [], 'timestamp': 1457446336.0, 'subfolder': [], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}], 'apiv': 1, 'direction': 'forward'}, {'forced': False, 'type': 'update', 'message': 'That missing camera lerp and a polestar mesh', 'rep': 'GitSpace', 'changes': [{'action': 'none', 'name': 'MainScreen', 'filetypes': [], 'timestamp': 1457527678.0, 'subfolder': [{'action': 'none', 'name': 'Assets', 'filetypes': [], 'timestamp': 1457527678.0, 'subfolder': [{'action': 'added', 'name': 'Materials', 'filetypes': [], 'timestamp': 1457527678.0, 'subfolder': [], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}, {'action': 'added', 'name': 'Resources', 'filetypes': [], 'timestamp': 1457527678.0, 'subfolder': [{'action': 'added', 'name': 'Materials', 'filetypes': [], 'timestamp': 1457527678.0, 'subfolder': [], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}, {'action': 'modified', 'name': 'Scripts', 'filetypes': [], 'timestamp': 1457527678.0, 'subfolder': [], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}], 'apiv': 1, 'direction': 'forward'}, {'forced': False, 'type': 'update', 'message': "Some root star improvement but WTF? It's super broken...", 'rep': 'GitSpace', 'changes': [{'action': 'none', 'name': 'MainScreen', 'filetypes': [], 'timestamp': 1457528134.0, 'subfolder': [{'action': 'none', 'name': 'Assets', 'filetypes': [], 'timestamp': 1457528134.0, 'subfolder': [{'action': 'modified', 'name': 'Materials', 'filetypes': [], 'timestamp': 1457528134.0, 'subfolder': [], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}, {'action': 'modified', 'name': 'Prefabs', 'filetypes': [], 'timestamp': 1457528134.0, 'subfolder': [], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}, {'action': 'modified', 'name': 'Scenes', 'filetypes': [], 'timestamp': 1457528134.0, 'subfolder': [], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}], 'user': 'decentninja', 'non_master_branch': False, 'size': 0}], 'apiv': 1, 'direction': 'forward'}, {'forced': False, 'type': 'update', 'message': 'delete function + other update fixes\n\nDeleting a folder is now possible. Creating folders works but the\ncreated folders have no glow.', 'rep': 'GitSpace', 'changes': [{'action': 'none', 'name': 'MainScreen', 'filetypes': [], 'timestamp': 1457556444.0, 'subfolder': [{'action': 'none', 'name': 'Assets', 'filetypes': [], 'timestamp': 1457556444.0, 'subfolder': [{'action': 'modified', 'name': 'Scripts', 'filetypes': [], 'timestamp': 1457556444.0, 'subfolder': [], 'user': 'matlon', 'non_master_branch': False, 'size': 0}], 'user': 'matlon', 'non_master_branch': False, 'size': 0}], 'user': 'matlon', 'non_master_branch': False, 'size': 0}], 'apiv': 1, 'direction': 'forward'}, {'forced': False, 'type': 'update', 'message': 'lightpower calc method', 'rep': 'GitSpace', 'changes': [{'action': 'none', 'name': 'MainScreen', 'filetypes': [], 'timestamp': 1457603102.0, 'subfolder': [{'action': 'none', 'name': 'Assets', 'filetypes': [], 'timestamp': 1457603102.0, 'subfolder': [{'action': 'modified', 'name': 'Scripts', 'filetypes': [], 'timestamp': 1457603102.0, 'subfolder': [], 'user': 'adhag', 'non_master_branch': False, 'size': 0}], 'user': 'adhag', 'non_master_branch': False, 'size': 0}], 'user': 'adhag', 'non_master_branch': False, 'size': 0}], 'apiv': 1, 'direction': 'forward'}]
	print("BEFORE")
	print_tree_structure(state['state'])
	for u in updates:
		print("UPDATE")
		print_tree_structure(u['changes'])
		update_state(state,[u])
		print("AFTER")
		print_tree_structure(state['state'])