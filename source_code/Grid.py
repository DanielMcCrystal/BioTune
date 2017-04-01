from midiutil.MidiFile import MIDIFile
import random
import source_code.Utils as utils

class Grid:
	def __init__(self, length, grid = None):
		self.grid = grid
		if grid is None:
			self.grid = [[None for i in range(24)] for j in range(length)]
		self.num_notes = len(self.grid)
		self.note_range = len(self.grid[0])
		self.lowest_note = 48

	def copy(self):
		return Grid(self.num_notes, grid = [list(col) for col in list(self.grid)])

	def add_note(self, pos, pitch, duration):
		self.grid[pos][pitch] = True
		for i in range(duration-1):
			self.grid[pos+1+i][pitch] = False

	def remove_note(self, pos, pitch):
		if not self.grid[pos][pitch]:
			return
		duration = 1
		next_cell = None
		if pos + duration < self.num_notes:
			next_cell = self.grid[pos + duration][pitch]
		while next_cell is not None and not next_cell:
			duration += 1
			if pos + duration < self.num_notes:
				next_cell = self.grid[pos + duration][pitch]
				self.grid[pos + duration][pitch] = None
			else:
				next_cell = None

	def populate_random(self):
		i = 0
		while i < self.num_notes:
			pos = random.randint(0, self.num_notes-1)
			pitch = random.randint(0, self.note_range-1)
			duration = random.randint(1, 8)
			if self.grid[pos][pitch] is None and pos + duration < self.num_notes:
				self.add_note(pos, pitch, duration)
				i += 1

	def convert_to_MIDI(self, title):
		mf = MIDIFile(1, adjust_origin=False)
		track = 0
		time = 0
		mf.addTrackName(track, time, title)
		mf.addTempo(track, time, 120)
		for pos in range(self.num_notes):
			for pitch in range(self.note_range):
				if self.grid[pos][pitch]:
					duration = 1
					next_cell = None
					if pos + duration < self.num_notes:
						next_cell = self.grid[pos + duration][pitch]
					while next_cell is not None and not next_cell:
						duration += 1
						if pos + duration < self.num_notes:
							next_cell = self.grid[pos + duration][pitch]
						else:
							next_cell = None
					mf.addNote(0, 0, pitch + self.lowest_note, pos, duration, 80)
		with open(title, 'wb') as outf:
			mf.writeFile(outf)
