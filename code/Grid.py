from midiutil.MidiFile import MIDIFile
MyMIDI = MIDIFile(1)
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
					offset = 1
					next_cell = self.grid[pos + offset][pitch]
					while next_cell is not None and not next_cell:
						duration += 1
						next_cell = self.grid[pos + offset]
					mf.addNote(0, 0, pitch + self.lowest_note, pos, duration, 80)
		with open(title, 'wb') as outf:
			mf.writeFile(outf)
