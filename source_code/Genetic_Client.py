import random
import source_code.Utils as utils
from source_code.Grid import Grid
import matplotlib.pyplot as plt
import numpy as np

class Genetic_Client_Chords:
	# Start with an initial population of variable size
	def __init__(self, population_size):
		self.generation = 0
		self.population = [[None for i in range(2)] for j in range(population_size)]
		self.tops = []
		self.expected_note_overlap = 3
		self.sd_note_overlap = 2
		expected = self.expected_note_overlap
		sd = self.sd_note_overlap
		self.max_note_overlap_score = utils.norm_pdf(expected, expected, sd)
		self.expected_chord_length = 4
		self.sd_chord_length = 2
		expected = self.expected_chord_length
		sd = self.sd_chord_length
		self.max_chord_length_score = utils.norm_pdf(expected, expected, sd)
		for i in range(population_size):
			grid = Grid(32)
			grid.populate_random_chords()
			self.population[i][0] = grid
			self.population[i][1] = self.chord_fitness(grid)


	# Determine the fitness of a particular chord specimen
	def chord_fitness(self, specimen):
		grid = specimen.grid
		fitness = 1.0

		col_chords = [None] * specimen.num_notes

		# Tier 1 setup
		last_chord = None
		scores1 = []

		# Tier 3 setup
		expected = self.expected_note_overlap
		sd = self.sd_note_overlap
		max_score = self.max_note_overlap_score
		scores3 = []

		# Tiers 1 and 3
		for col in range(specimen.num_notes):
			# generate list of notes in chord
			notes_in_col = []
			for i in range(specimen.note_range):
				if grid[col][i] is not None:
					notes_in_col.append(i)
			if len(notes_in_col) == 0:
				continue
			lowest_note = notes_in_col[0]

			# generate possible chords for the column
			possible_chords = [utils.get_triad(lowest_note, type) for type in range(3)]
			if last_chord is not None and last_chord not in possible_chords:
				possible_chords.append(last_chord)

			# find the ratio of notes in each chord
			ratios = [None] * len(possible_chords)
			for chord in range(len(possible_chords)):
				count = 0
				for note in notes_in_col:
					if utils.note_in_set(note, possible_chords[chord]):
						count += 1
				ratios[chord] = float(count) / len(notes_in_col)
			best_ratio = max(ratios)
			scores1.append(best_ratio)
			best_chord = possible_chords[ratios.index(best_ratio)]
			col_chords[col] = best_chord
			last_chord = best_chord

			# Do Tier 3 stuff
			count = len(notes_in_col)
			scores3.append(utils.norm_pdf(count, expected, sd) / max_score)


		specimen.col_chords = col_chords
		multiplier1 = (utils.geometric_mean(scores1) * 2) ** 5
		fitness *= multiplier1
		multiplier3 = utils.geometric_mean(scores3) * 2
		fitness *= multiplier3

		# Tier 2 (Chord Changing)
		chord_sequence = utils.compact_chord_cols(col_chords)
		scores2 = [None] * len(chord_sequence)
		expected = self.expected_chord_length
		sd = self.sd_chord_length
		max_score = self.max_chord_length_score
		for i in range(len(chord_sequence)):
			chord = chord_sequence[i]
			scores2[i] = utils.norm_pdf(chord[1], expected, sd) / max_score

		multiplier2 = utils.geometric_mean(scores2) * 2
		fitness *= multiplier2

		# Tier 4 (Key)
		keys = [None] * 24
		for i in range(12):
			keys[i] = utils.chords_in_key(i, 0)
			keys[i + 12] = utils.chords_in_key(i, 1)
		max_count = 0
		for key in keys:
			count = 0
			for chord in chord_sequence:
				if utils.is_chord_in_key(chord[0], key):
					count += 1
			if count > max_count:
				max_count = count
		ratio = max_count / len(chord_sequence)
		multiplier = ratio * 2
		fitness *= multiplier

		return fitness

	# Calculate fitness of each specimen in the population
	# Print top fitness, average fitness
	# Kill bottom 50%
	# Repopulate with offspring of top 50%
	def darwin(self):
		self.population.sort(key=lambda x: x[1])
		print("Top fitness: " + str(self.best_fitness()))
		self.tops[self.generation] = self.best_fitness()
		avg = self.avg_fitness()
		print("Average fitness: " + str(avg))
		half = int(len(self.population) / 2)
		survivors = range(half, len(self.population))
		for i in survivors:
			offspring = self.offspring(self.population[i][0])
			self.population[i-half] = [offspring, self.chord_fitness(offspring)]
		print("Simulated gen " + str(self.generation))
		self.generation = self.generation + 1

	def avg_fitness(self):
		sum = 0
		for individual in self.population:
			sum += individual[1]
		return sum / len(self.population)

	def best_fitness(self):
		return self.population[len(self.population) - 1][1]

	def best_individual(self):
		return self.population[len(self.population)-1][0]

	# Generate an offspring of a particular specimen with random mutations
	def offspring(self, specimen):
		grid = specimen.grid
		offspring = specimen.copy()
		mutation = random.random()
		if mutation < 0.05: # add new note
			pos = random.randint(0, offspring.num_notes - 1)
			pitch = random.randint(0, offspring.note_range - 1)
			duration = random.randint(2, 6)
			offspring.add_note(pos, pitch, duration)
			return offspring
		n = random.randint(1, specimen.note_count)
		track = 0
		done = False
		for pos in range(specimen.num_notes):
			for pitch in range(specimen.note_range):
				if grid[pos][pitch]:
					track += 1
					if track == n:
						offspring.remove_note(pos, pitch) # 5% chance to only remove note
						if mutation < 0.95:  # move note
							pos_movement = random.randint(-3, 3)
							if pos + pos_movement < 0 or pos + pos_movement >= specimen.num_notes:
								pos_movement = 0
							pitch_movement = random.randint(-5, 5)
							if pitch + pitch_movement < 0 or pitch + pitch_movement >= specimen.note_range:
								pitch_movement = 0
							new_duration = random.randint(2, 6)
							offspring.add_note(pos + pos_movement, pitch + pitch_movement, new_duration)
						done = True
						break
			if done:
				break

		return offspring


class Genetic_Client_Melody:
	# Start with an initial population of variable size
	def __init__(self, population_size, chord_specimen, lines):
		self.lines = lines
		self.chord_specimen = chord_specimen
		self.col_chords = [None] * chord_specimen.num_notes
		last_chord = None
		for col in range(chord_specimen.num_notes):
			# generate list of notes in chord
			notes_in_col = []
			for i in range(self.chord_specimen.note_range):
				if chord_specimen.grid[col][i] is not None:
					notes_in_col.append(i)
			if len(notes_in_col) == 0:
				continue
			lowest_note = notes_in_col[0]

			# generate possible chords for the column
			possible_chords = [utils.get_triad(lowest_note, type) for type in range(3)]
			if last_chord is not None and last_chord not in possible_chords:
				possible_chords.append(last_chord)

			# find the ratio of notes in each chord
			ratios = [None] * len(possible_chords)
			for chord in range(len(possible_chords)):
				count = 0
				for note in notes_in_col:
					if utils.note_in_set(note, possible_chords[chord]):
						count += 1
				ratios[chord] = float(count) / len(notes_in_col)
			best_ratio = max(ratios)
			best_chord = possible_chords[ratios.index(best_ratio)]
			self.col_chords[col] = best_chord
			last_chord = best_chord

		self.generation = 0
		self.population = [[None for i in range(2)] for j in range(population_size)]
		self.tops = []
		self.expected_note_overlap = 1  # TODO: change back to 4
		self.sd_note_overlap = 2
		expected = self.expected_note_overlap
		sd = self.sd_note_overlap
		self.max_note_overlap_score = utils.norm_pdf(expected, expected, sd)
		self.expected_chord_length = 4
		self.sd_chord_length = 2
		expected = self.expected_chord_length
		sd = self.sd_chord_length
		self.max_chord_length_score = utils.norm_pdf(expected, expected, sd)
		for i in range(population_size):
			grid = Grid(32)
			grid.populate_random_melody(lines)  # [[slope, number of grid cells], ...])
			self.population[i][0] = grid
			self.population[i][1] = self.melody_fitness(grid)



	# Determine the fitness of a particular chord specimen
	def melody_fitness(self, specimen):
		grid = specimen.grid
		fitness = 1.0

		# Tier 1 setup
		scores1 = []

		# Tier 3 setup
		expected = self.expected_note_overlap
		sd = self.sd_note_overlap
		max_score = self.max_note_overlap_score
		scores3 = []

		# Tier 5 setup (COWBOY'S STUFF)
		current_base_note = None  # the base note of where the slope started
		x_dist = 0  # how many grid cells we are away from the base node
		line_index = 0  # indexes into the slopes array
		scores5 = []

		# Tiers 1 and 3 AND 5
		for col in range(specimen.num_notes):
			current_chord = self.col_chords[col]
			current_scale = utils.get_double_scale(current_chord)

			# generate list of notes in col
			notes_in_col = []
			for i in range(self.chord_specimen.note_range):
				if grid[col][i] is not None:
					notes_in_col.append(i)
			if len(notes_in_col) == 0:
				continue

			# find the ratio of notes in each chord
			count = 0
			for note in notes_in_col:
				if utils.note_in_set(note, current_chord):  # TODO: use the right util function
					count += 1
			ratio = float(count) / len(notes_in_col)
			scores1.append(ratio)

			# Do Tier 3 stuff
			count = len(notes_in_col)
			scores3.append(utils.norm_pdf(count, expected, sd) / max_score)

			# Do Tier 5 stuff
			if line_index < len(self.lines):
				line = self.lines[line_index]
				current_avg = sum(notes_in_col) / len(notes_in_col)
				if x_dist >= line[1]:
					# switch to next line
					line_index += 1
					current_base_note = current_avg
					x_dist = 0
				else:
					slope = line[0]
					expected_note = slope * x_dist + current_base_note
					diff = (expected_note - current_avg)**2
					value = np.tanh(diff/25)
					scores5.append(1 - value)

				x_dist += 1

		# multiplier1 = (utils.geometric_mean(scores1) * 2) ** 5
		multiplier1 = sum(scores1) / len(scores1) * 2
		fitness *= multiplier1
		multiplier3 = utils.geometric_mean(scores3) * 2
		fitness *= multiplier3
		multiplier5 = utils.geometric_mean(scores5) * 2
		fitness *= multiplier5

		return fitness

	# Calculate fitness of each specimen in the population
	# Print top fitness, average fitness
	# Kill bottom 50%
	# Repopulate with offspring of top 50%
	def darwin(self):
		self.population.sort(key=lambda x: x[1])
		print("Top fitness: " + str(self.best_fitness()))
		self.tops[self.generation] = self.best_fitness()
		avg = self.avg_fitness()
		print("Average fitness: " + str(avg))
		half = int(len(self.population) / 2)
		survivors = range(half, len(self.population))
		for i in survivors:
			offspring = self.offspring(self.population[i][0])
			self.population[i-half] = [offspring, self.melody_fitness(offspring)]
		print("Simulated gen " + str(self.generation))
		self.generation = self.generation + 1

	def avg_fitness(self):
		sum = 0
		for individual in self.population:
			sum += individual[1]
		return sum / len(self.population)

	def best_fitness(self):
		return self.population[len(self.population) - 1][1]

	def best_individual(self):
		return self.population[len(self.population)-1][0]

	# Generate an offspring of a particular specimen with random mutations
	def offspring(self, specimen):
		grid = specimen.grid
		offspring = specimen.copy()
		mutation = random.random()
		if mutation < 0.05: # add new note
			pos = random.randint(0, offspring.num_notes - 1)
			pitch = random.randint(0, offspring.note_range - 1)
			duration = random.randint(1, 3)
			offspring.add_note(pos, pitch, duration)
			return offspring
		n = random.randint(1, specimen.note_count)
		track = 0
		done = False
		for pos in range(specimen.num_notes):
			for pitch in range(specimen.note_range):
				if grid[pos][pitch]:
					track += 1
					if track == n:
						offspring.remove_note(pos, pitch) # 5% chance to only remove note
						if mutation < 0.95:  # move note
							pos_movement = random.randint(-3, 3)
							if pos + pos_movement < 0 or pos + pos_movement >= specimen.num_notes:
								pos_movement = 0
							pitch_movement = random.randint(-5, 5)
							if pitch + pitch_movement < 0 or pitch + pitch_movement >= specimen.note_range:
								pitch_movement = 0
							new_duration = random.randint(2, 6)
							offspring.add_note(pos + pos_movement, pitch + pitch_movement, new_duration)
						done = True
						break
			if done:
				break

		return offspring



if __name__ == '__main__':
	# Generate the chords
	gc_chords = Genetic_Client_Chords(150)
	gc_chords.population[0][0].convert_to_MIDI("../outputs/start.mid")
	inpt = input("Chords: How many generations should I simulate? ")
	while not inpt == 'done':
		gc_chords.tops += [None] * int(inpt)
		for i in range(int(inpt)):
			gc_chords.darwin()
		inpt = input("Chords: How many generations should I simulate? ")
	print("Fitness: " + str(gc_chords.best_fitness()))
	# plt.plot(gc_chords.tops)
	# plt.show()
	gc_chords.best_individual().convert_to_MIDI("../outputs/best_chords.mid")

	# Generate the melody
	lines = [[None, 0], [4, 5], [-2, 5], [1, 10], [-1, 3], [-2, 7]]
	gc_melody = Genetic_Client_Melody(150, gc_chords.best_individual(), lines)
	gc_melody.population[0][0].convert_to_MIDI("../outputs/start.mid")
	inpt = input("Melody: How many generations should I simulate? ")
	while not inpt == 'done':
		gc_melody.tops += [None] * int(inpt)
		for i in range(int(inpt)):
			gc_melody.darwin()
		inpt = input("Melody: How many generations should I simulate? ")
	print("Fitness: " + str(gc_melody.best_fitness()))

	# gc_melody.best_individual().populate_random_melody()
	gc_melody.best_individual().convert_to_MIDI("../outputs/best_melody.mid")
	plt.plot(gc_melody.tops)
	plt.show()
