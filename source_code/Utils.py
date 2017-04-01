import math

def notes_equal(a, b):
	return a % 12 == b % 12

def get_triad(pitch, type):
	triad = [pitch]
	if type == 0: # major
		triad.append(pitch + 4)
		triad.append(pitch + 7)
	elif type == 1: # minor
		triad.append(pitch + 3)
		triad.append(pitch + 7)
	elif type == 2: # diminished
		triad.append(pitch + 3)
		triad.append(pitch + 6)

	return triad

def note_in_set(pitch, set):
	if set is None:
		return False
	for note in set:
		if notes_equal(pitch, note):
			return True
	return False

def is_chord_in_key(chord, key): # key is a list of chords
	for key_chord in key:
		if chords_equal(key_chord, chord):
			return True
	return False

def chords_equal(chord1, chord2):
	for note in chord1:
		if not note_in_set(note, chord2):
			return False
	return True


def chords_in_key(pitch, type):

	if type == 0: # major
		scale_pattern = 'wwhwww'
		type_pattern = [1, 1, 0, 0, 1, 2]
	elif type == 1: # minor
		scale_pattern = 'whwwhw'
		type_pattern = [2, 0, 1, 1, 0, 0]
	note = pitch
	chords = [None] * 7
	chords[0] = get_triad(pitch, type)
	for i in range(len(scale_pattern)):
		if scale_pattern[i] == 'w':
			note += 2
		elif scale_pattern[i] == 'h':
			note += 1
		chords[i + 1] = get_triad(note, type_pattern[i])
	return chords

def geometric_mean(set):
	prod = 1
	for item in set:
		prod *= item
	return prod ** (1 / float(len(set)))

def compact_chord_cols(chords):
	compact = []
	last = None
	count = 0
	for chord in chords:
		count += 1
		if not chord == last:
			if last is not None:
				compact.append([last, count])
			last = chord
			count = 0
	count += 1
	compact.append([last, count])
	return compact

def norm_pdf(x, mean, sd):
	var = float(sd) ** 2
	denom = math.sqrt(2 * math.pi * var)
	num = math.exp(-(float(x) - float(mean)) ** 2 / (2 * var))
	return num / denom