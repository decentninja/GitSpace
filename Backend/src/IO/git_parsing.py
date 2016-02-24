import os.path

# Constants
# Could be translated to properties
__version = 1
__supported_versions = [1]

def raw_to_state(raw_state, API_version = None):
	if API_version == None:
		API_version = __version
	if API_version not in __supported_versions:
		raise Exception('Unknown API version: ' + API_version)
	if API_version == 1:
		state = {}
		state['api version'] = 1
		state['type'] = 'state'
		state['repo'] = 'PLACEHOLDER' # TODO placeholder
		state['timestamp'] = 52341414 # TODO placeholder
		state['state'] = _extract_folders(raw_state['tree'],API_version)
		with open("output.txt","w+") as f:
			def print_tree(depth,tree):
				for t in tree:
					print("  "*depth+t['name'],t['size'],t['filetypes'],file=f)
					print_tree(depth+1,t["subfolder"])
			print_tree(0,state['state'])
		return state

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

if __name__ == '__main__':
	from gitinput import myinput
	raw_to_state(myinput)