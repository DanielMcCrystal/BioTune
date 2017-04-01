from midiutil.MidiFile import MIDIFile
import random

class Grid:
	def __init__(self, length):
		self.grid = [[None for i in range(24)] for j in range(length)]
		self.num_notes = len(self.grid)
		self.note_range = len(self.grid[0])
		self.lowest_note = 48

	def add_note(self, position, pitch, duration):
		self.grid[position][pitch] = True
		for i in range(duration-1):
			self.grid[position+1+i][pitch] = False

	def populate_random(self):
		i = 0
		while i < 96:
			pos = random.randint(0, self.num_notes-1)
			pitch = random.randint(0, self.note_range-1)
			duration = random.randint(1, 16)
			if self.grid[pos][pitch] is None and pos + duration < self.num_notes:
				self.add_note(pos, pitch, duration)
				i += 1

	def melody(self, pitch, position):
		pitch = pitch.grid
		position = position.grid
		pitch.grid = [0,]
		position.grid = [position]

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
					next_cell = self.grid[pos + duration][pitch]
					while next_cell is not None and not next_cell:
						duration += 1
						next_cell = self.grid[pos + duration][pitch]
					print(duration)
					mf.addNote(0, 0, pitch + self.lowest_note, pos, duration, 80)
		with open(title, 'wb') as outf:
			mf.writeFile(outf)

g = Grid(96)
g.populate_random()
g.convert_to_MIDI("test.mid")
print("done")