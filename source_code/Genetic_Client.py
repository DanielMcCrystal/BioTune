import random,
import source_code.Utils as utils
from source_code.Grid import Grid

class Genetic_Client:
	# Start with an initial population of variable size
	def __init__(self, population_size):
		self.generation = 1

		pass

	# Determine the fitness of a particular chord specimen
	def chord_fitness(self, specimen):
		grid = specimen.grid
		fitness = 1.0

		col_chords = [None] * specimen.num_notes

		# Tier 1 (Individual Columns)
		last_chord = None
		tier_1_scores = []
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
			tier_1_scores.append(best_ratio)
			best_chord = possible_chords[ratios.index(best_ratio)]
			col_chords[col] = best_chord
			last_chord = best_chord
		multiplier = utils.geometric_mean(tier_1_scores) * 2
		print(multiplier)
		fitness *= multiplier

		# Tier 2 (Chord Changing)


		return fitness

	# Calculate fitness of each specimen in the population
	# Print top fitness, average fitness
	# Kill bottom 50%
	# Repopulate with offspring of top 50%
	def darwin(self):
		print("Simulated gen " + str(self.generation))
		self.generation = self.generation + 1
		pass

	# Generate an offspring of a particular specimen with random mutations
	def offspring(self, specimen):
		grid = specimen.grid
		offspring = [list(col) for col in list(grid)]
		for pos in range(grid.num_notes):
			for pitch  in range(grid.note_range):
				if grid[pos][pitch]:
					if random.random() < .0001:
						pos_movement = random.randint(-2, 2)
						if pos + pos_movement < 0 or pos + pos_movement >= grid.num_notes:
							pos_movement = 0
						pitch_movement = random.randint(-2, 2)
						if pitch + pitch_movement < 0 or pitch + pitch_movement >= grid.note_range:
							pitch_movement = 0
						new_duration = random.randint(1, 16)
						if pos + pos_movement + new_duration >= grid.num_notes - 1:
							new_duration = 1
						offspring.remove_note(pos, pitch)
						offspring.add_note(pos + pos_movement, pitch + pitch_movement, new_duration)

		return offspring


if __name__ == '__main__':
	gc = Genetic_Client(1000)
	inpt = input("How many generations should I simulate? ")
	while(inpt != "done"):
		for i in range(int(inpt)):
			gc.darwin()
		inpt = input("How many generations should I simulate? ")
