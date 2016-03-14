import IO.git_io
import IO.git_parsing

class Repository:

	def __init__(self,repo,lookback = 21):
		state,updates = IO.git_io.get_init(repo)
		self.user_states = {None: state}
		self.lookback_value = lookback
		self.contributors = git_io.get_collabotators(repo)
		self.name = repo
		names = [c['username'] for c in self.contributors]

		#TODO CREATE STATES FOR USERS
		# self.user_states+=create_user_states(self.user_states[None],names)
		apply_updates()


	def get_latest_state(self,user = None):
		return self.user_states.get(user)

	def get_user_update(user):
		state = get_latest_state(user)
		if not state:
			raise Exception("ERROR: user %s missing in repo %s"%(user,self.name))
		return git_parsing.state_to_update(state)

	def comm_format():
		return {'name': self.name, 'users': self.contributors}

	def apply_updates(self, updates):
		git_parsing.update_user_states(self.user_states,updates)		

	

if __name__ == '__main__':
	a = Repository("decentninja/GitSpace",lookback = 7)
	print(a.get_latest_state())
	print(a.get_user_update(None))
	print(comm_format())
