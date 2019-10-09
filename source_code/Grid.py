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
		self.note_count = 0
		self.col_chords = None

	def copy(self):
		copied = Grid(self.num_notes, grid = [list(col) for col in list(self.grid)])
		copied.note_count = self.note_count
		return copied

	def add_note(self, pos, pitch, duration):
		if pos < 0 or pos >= self.num_notes or pitch < 0 or pitch >= self.note_range:
			return
		if self.grid[pos][pitch]:
			self.note_count -= 1
		else:
			self.grid[pos][pitch] = True
		for i in range(duration-1):
			new_pos = pos + 1 + i
			if new_pos >= self.num_notes or self.grid[new_pos][pitch] is not None:
				break
			self.grid[new_pos][pitch] = False
		self.note_count += 1

	def remove_note(self, pos, pitch):
		if not self.grid[pos][pitch]:
			return
		self.grid[pos][pitch] = None
		duration = 1
		next_cell = None
		if pos + duration < self.num_notes:
			next_cell = self.grid[pos + duration][pitch]
		while next_cell == False:
			duration += 1
			if pos + duration < self.num_notes:
				next_cell = self.grid[pos + duration][pitch]
				self.grid[pos + duration][pitch] = None
			else:
				next_cell = None
		self.note_count -= 1

	def populate_random_chords(self):
		i = 0
		while i < self.num_notes * 2:
			pos = random.randint(0, self.num_notes-1)
			pitch = random.randint(0, self.note_range-1)
			duration = random.randint(2, 6)
			if self.grid[pos][pitch] is None and pos + duration < self.num_notes:
				self.add_note(pos, pitch, duration)
				i += 1

	def populate_random_melody(self, lines):
		pos = 0

		current_base_note = None  # the base note of where the slope started
		x_dist = 0  # how many grid cells we are away from the base node
		line_index = 0  # indexes into the slopes array
		last_note = 0

		while pos < self.num_notes:
			if line_index < len(lines):
				line = lines[line_index]
				if x_dist >= line[1]:
					# switch to next line
					line_index += 1
					current_base_note = last_note
					x_dist = 0
				else:
					duration = random.randint(1, 3)
					slope = line[0]
					expected_note = slope * x_dist + current_base_note
					self.add_note(pos, expected_note + random.randint(-2, 2), duration)
					# self.add_note(pos, expected_note, duration)
					last_note = expected_note

				x_dist += 1
			pos += 1


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
					mf.addNote(0, 0, pitch + self.lowest_note, pos, duration, 60)
		with open(title, 'wb') as outf:
			mf.writeFile(outf)
