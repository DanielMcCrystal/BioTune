from midiutil.MidiFile import MIDIFile
MyMIDI = MIDIFile(1)
class Grid:
    def __init__(self, length):
        self.grid = [[None]* 24] * length

    def add_note(self, position, pitch, duration):
        self.grid[position][pitch] = True
        for i in range(duration-1):
            self.grid[position+1+i][pitch] = False

    def melody(self, pitch, position):
        pitch = pitch.grid
        position = position.grid
        pitch.grid = [0,]
        position.grid = [position]


for pitch in Grid:
    MyMIDI.addNote(position, pitch, duration)
    time = time + 1

with open("major-scale.mid", "wb") as output_file:
    MyMIDI.writeFile(output_file)
