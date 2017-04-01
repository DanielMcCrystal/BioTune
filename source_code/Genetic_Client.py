import random
import source_code.Utils as utils
from source_code.Grid import Grid

class Genetic_Client:
	# Start with an initial population of variable size
	def __init__(self, population_size):
		self.generation = 1
		self.population = [[None for i in range(2)] for j in range(population_size)]
		for i in range(population_size):
			grid = Grid(48)
			grid.populate_random()
			self.population[i][0] = grid
			self.population[i][1] = self.chord_fitness(grid)

	# Determine the fitness of a particular chord specimen
	def chord_fitness(self, specimen):
		grid = specimen.grid
		fitness = 1.0

		col_chords = [None] * specimen.num_notes

		# Tier 1 (Individual Columns)
		last_chord = None
		scores = []
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
			possible_chords = [utils.get_triad(lowest_note, type) for type in range(4)]
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
			scores.append(best_ratio)
			best_chord = possible_chords[ratios.index(best_ratio)]
			col_chords[col] = best_chord
			last_chord = best_chord
		multiplier = (utils.geometric_mean(scores) * 2) ** 4
		fitness *= multiplier

		# Tier 2 (Chord Changing)
		chord_sequence = utils.compact_chord_cols(col_chords)
		scores = [None] * len(chord_sequence)
		expected = 8
		sd = 4
		max_score = utils.norm_pdf(expected, expected, sd)
		for i in range(len(chord_sequence)):
			chord = chord_sequence[i]
			scores[i] = utils.norm_pdf(chord[1], expected, sd) / max_score

		multiplier = utils.geometric_mean(scores) * 2
		fitness *= multiplier

		# Tier 3 (Overlap)
		expected = 4
		sd = 1
		scores = [None] * specimen.num_notes
		max_score = utils.norm_pdf(expected, expected, sd)
		for col in range(specimen.num_notes):
			count = 0
			for pitch in range(specimen.note_range):
				if grid[col][pitch] is not None:
					count += 1
			scores[col] = utils.norm_pdf(count, expected, sd)
		multiplier = utils.geometric_mean(scores) * 2
		fitness *= multiplier

		# Tier 4 (Key)
		

		return fitness

	# Calculate fitness of each specimen in the population
	# Print top fitness, average fitness
	# Kill bottom 50%
	# Repopulate with offspring of top 50%
	def darwin(self):
		self.population = sorted(self.population, key=lambda x: x[1])
		print("Top fitness: " + str(self.population[len(self.population)-1][1]))
		print("Average fitness: " + str(self.avg_fitness()))
		survivors = range(int(len(self.population) / 2), len(self.population))
		deaths = range(int(len(self.population) / 2))
		offsprings = [self.offspring(self.population[i][0]) for i in survivors]
		for i in deaths:
			self.population[i] = [offsprings[i], self.chord_fitness(offsprings[i])]
		print("Simulated gen " + str(self.generation))
		self.generation = self.generation + 1

	def avg_fitness(self):
		sum = 0
		for individual in self.population:
			sum += individual[1]
		return sum / len(self.population)

	def best_individual(self):
		return self.population[len(self.population)-1][0]

	# Generate an offspring of a particular specimen with random mutations
	def offspring(self, specimen):
		grid = specimen.grid
		offspring = specimen.copy()
		for pos in range(specimen.num_notes):
			for pitch  in range(specimen.note_range):
				if grid[pos][pitch]:
					if random.random() < .05:
						pos_movement = random.randint(-4, 4)
						if pos + pos_movement < 0 or pos + pos_movement >= specimen.num_notes:
							pos_movement = 0
						pitch_movement = random.randint(-4, 4)
						if pitch + pitch_movement < 0 or pitch + pitch_movement >= specimen.note_range:
							pitch_movement = 0
						new_duration = random.randint(1, 8)
						if pos + pos_movement + new_duration >= specimen.num_notes - 1:
							new_duration = 1
						offspring.remove_note(pos, pitch)
						offspring.add_note(pos + pos_movement, pitch + pitch_movement, new_duration)

		return offspring


if __name__ == '__main__':
	gc = Genetic_Client(100)
	# gc.population[0][0].convert_to_MIDI("../outputs/start.mid")
	inpt = input("How many generations should I simulate? ")
	while(inpt != "done"):
		for i in range(int(inpt)):
			gc.darwin()
		inpt = input("How many generations should I simulate? ")
	gc.best_individual().convert_to_MIDI("../outputs/best.mid")
