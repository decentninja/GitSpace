import IO.git_io as git_io
import IO.git_parsing as git_parsing

class Repository:

	def __init__(self,repo,lookback = 21):
		state,updates = git_io.get_init(repo)
		self.user_states = {None: state}
		self.lookback_value = lookback
		self.contributors = git_io.get_collaborators(repo)
		self.name = repo
		self.latest_sha = ""
		names = [c['username'] for c in self.contributors]

		#TODO CREATE STATES FOR USERS
		self.user_states.update(git_parsing.create_user_states(self.user_states[None],names))
		self.apply_updates(updates)


	def get_latest_state(self,user = None):
		return self.user_states.get(user)

	def get_user_update(self,user):
		state = self.get_latest_state(user)
		if not state:
			raise Exception("ERROR: user %s missing in repo %s"%(user,self.name))
		return git_parsing.state_to_update(state)

	def comm_format(self):
		return {'name': self.name, 'users': self.contributors}

	def apply_updates(self, updates):
	#	if (self.latest_sha in [u['sha'] for u in updates]):
	#		print("WARNING: commit already applied onto repo")
		self.latest_sha = updates[-1]['sha']
		git_parsing.update_user_states(self.user_states,updates)		

	

if __name__ == '__main__':
	a = Repository("decentninja/GitSpace",lookback = 7)
	for k,v in a.user_states.items():
		print(k)
		git_parsing.print_tree_structure(v['state'],['name','last modified by','last modified date'])
