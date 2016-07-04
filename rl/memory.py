from collections import deque, namedtuple
import numpy as np


# This is to be understood as a transition: Given `state0`, performing `action`
# yields `reward` and results in `state1`, which might be `terminal`.
Experience = namedtuple('Experience', 'state0, action, reward, terminal, state1')


class RingBuffer(object):
	def __init__(self, maxlen):
		self.maxlen = maxlen
		self.start = 0
		self.length = 0
		self.data = [None for _ in xrange(maxlen)]

	def __len__(self):
		return self.length

	def __getitem__(self, idx):
		if idx < 0 or idx >= self.length:
			raise KeyError()
		return self.data[(self.start + idx) % self.maxlen]

	def append(self, v):
		if self.length < self.maxlen:
			# We have space, simply increase the length.
			self.length += 1
		elif self.length == self.maxlen:
			# No space, "remove" the first item.
			self.start = (self.start + 1) % self.maxlen
		else:
			# This should never happen.
			raise RuntimeError()
		self.data[(self.start + self.length - 1) % self.maxlen] = v


class Memory(object):
	def __init__(self, limit):
		self.limit = limit

		# Do not use deque to implement the memory. This data structure may seem convenient but
		# it is way too slow on random access. Instead, we use our own ring buffer implementation.
		self.actions = RingBuffer(limit)
		self.rewards = RingBuffer(limit)
		self.terminals = RingBuffer(limit)
		self.observations = RingBuffer(limit)

	def sample(self, batch_size, window_length):
		# Draw random indexes such that we have at least `window_length` entries before each index.
		batch_idxs = np.random.random_integers(window_length, self.nb_entries - 1, size=batch_size)
		assert len(batch_idxs) == batch_size
		
		# Create experiences
		experiences = []
		for idx in batch_idxs:
			state0 = [self.observations[i] for i in xrange(idx - window_length, idx)]
			action = self.actions[idx - 1]
			reward = self.rewards[idx - 1]
			terminal = self.terminals[idx - 1]
			state1 = [self.observations[i] for i in xrange(idx - window_length + 1, idx + 1)]
			assert len(state0) == window_length
			assert len(state1) == len(state0)
			experiences.append(Experience(state0, action, reward, terminal, state1))
		assert len(experiences) == batch_size
		return experiences

	def append(self, observation, action, reward, terminal):
		self.observations.append(observation)
		self.actions.append(action)
		self.rewards.append(reward)
		self.terminals.append(terminal)

	@property
	def nb_entries(self):
		return len(self.observations)