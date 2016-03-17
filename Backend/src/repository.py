import IO.git_io as git_io
import IO.git_parsing as git_parsing

import datetime

class Repository:

	def __init__(self,repo,lookback = 21):
		self.original_state, self.updates = git_io.get_init(repo)
		self.user_states = {None: self.original_state}
		self.lookback_value = lookback
		self.contributors = git_io.get_collaborators(repo)
		self.name = repo
		self.latest_sha = ""
		names = [c['username'] for c in self.contributors]

		#TODO CREATE STATES FOR USERS
		self.user_states.update(git_parsing.create_user_states(self.user_states[None],names))
		self.apply_updates(self.updates)


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
	#	self.latest_sha = updates[-1]['sha']
		git_parsing.update_user_states(self.user_states,updates)

	def empty_update(self):
		update = {}
		update['type'] = 'update'
		update['repo'] = 'GitSpace' # TODO placeholder
        update['real_time'] = False
		update['apiv'] = 1
		update['message'] = ''
		update['direction'] = 'forward'
		update['forced'] = False
		update['changes'] = []
		update["check_threshold"] = False
		return update

	def get_updates_before(self, next_time, i=0):
		update_list = []
		while (update_time < next_time and i < len(self.updates)):
		    update_time = datetime.datetime.fromtimestamp(self.updates[i]['timestamp'])
		    update_list.append(self.updates[i])
		    i =+ 1
		return update_list, i

	def get_rewind_list(self, minutes):
		rewind_list = []
		o_state = git_parsing._state_clone(self.original_state)
		time_now = datetime.datetime.now()
		next_time = time_now - datetime.timedelta(minutes=minutes)
		update_list, i = get_updates_before(next_time)
		git_parsing.update_state(o_state, update_list)
		rewind_list.append(git_parsing._state_clone(o_state))
		while (next_time < time_now):
			next_time = next_time + datetime.timedelta(hours=5)
			update_list, i = get_updates_before(next_time, i)
			if len(update_list) < 1:
				rewind_list.append(rewind_list(self.empty_update()))
			else:
				git_parsing.update_state(o_state, update_list)
				rewind_list.append(git_parsing.state_to_update(o_state))
        rewind_list[-1]['real_time'] = True
		return rewind_list

if __name__ == '__main__':
	a = Repository("decentninja/GitSpace",lookback = 7)
	for k,v in a.user_states.items():
		print(k)
		git_parsing.print_tree_structure(v['state'],['name','last modified by','last modified date'])
