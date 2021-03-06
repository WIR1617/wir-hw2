import pprint as pp
import sys

import pagerank_utils as pru
import topic_specific_pagerank as tspr
import configurations as conf



def _print_usage():
	usage='''
Usage:
	python WebIR_HW_2_part_3_offline.py <graph_path> <categories_path> <out_dir> [--verbose]
	OR
	python WebIR_HW_2_part_3_offline.py --default-config [--verbose]

Example:
	python WebIR_HW_2_part_3_offline.py ./datasets/movie_graph.txt ./datasets/category_movies.txt ./datasets --verbose
	OR
	python WebIR_HW_2_part_3_offline.py --default-config
	'''
	print(usage)


def compute_pageranks_by_category(movie_graph, category_movies_dict):
	"""
	From a movie graph and a dictionary {category_id : [movie_ids]}
	compute |C| pageranks, where C is the set of cotegories (i.e. the set of lines)
	In other words, execute |C| times (the number of categories) the pagerank algorithm
	topic-based (i.e. the teleporting probability distribution is positive and uniform only
	on movie belonging to the category of a given iteration, while the p.m.f. is zero over the
	rest of movies)
	:param movie_graph_filepath:
	:param category_movies_filepath:
	:return:
	"""
	result = {}

	categories = category_movies_dict.keys()

	for category_id in categories:
		# get subgraph from movies of category_id
		cur_category_subgraph = movie_graph.subgraph(category_movies_dict[category_id])

		# uniform distribution ONLY on movies belonging to the category; probabilities for other movies are set to zero.
		cur_teleporting_distribution = pru.get_uniform_teleporting_distribution_on_subgraph(movie_graph, cur_category_subgraph)

		# compute pagerank on the entire movie_graph for the current category (i.e. the current teleporting p.m.f)
		cur_pagerank = tspr.compute_topic_specific_pagerank(movie_graph, teleporting_distribution=cur_teleporting_distribution)

		# sort by score
		cur_pagerank_sorted = sorted(cur_pagerank.items(), key=lambda x: -x[1])

		# store the result in the result dictionary
		result[category_id] = cur_pagerank_sorted

	return result


def main(movie_graph_filepath, category_movies_filepath, output_dir):
	"""
	Compute the pagerank topic-based over every category and save each list of tuple (movie_id, score)
	in files whose filepath is "${output_dir}/pagerank_${category_id}"
	:param movie_graph_filepath:
	:param category_movies_filepath:
	:param output_dir:
	:return:
	"""

	movie_graph = pru.read_movie_graph(movie_graph_filepath)
	category_movies_dict = pru.read_category_movies(category_movies_filepath)


	category2pagerank = compute_pageranks_by_category(movie_graph, category_movies_dict)


	for category_id in category2pagerank:
		output_filepath = conf.PART_2_OUTPUT_DIR + conf.PART_2_PAGERANK_OUTPUT_FILENAME_FORMAT
		output_filepath = output_filepath.format(category_id)
		with open(output_filepath, "w") as fout:
			# write the topic-based pagerank (uniform teleporting probability over movies of the category)
			pru.print_pagerank_list(category2pagerank[category_id], file=fout)



if __name__ == '__main__':

	if len(sys.argv)>=4 and len(sys.argv)<=5:
		movie_graph_filepath = sys.argv[1]
		movie_categories_path = sys.argv[2]
		output_dir = sys.argv[3]

		if len(sys.argv)==5 and sys.argv[4]=="--verbose": verbose=True

	elif len(sys.argv) >= 2 and len(sys.argv) <= 3 and sys.argv[1] == "--default-config":
		movie_graph_filepath = conf.DATA_DIR + conf.MOVIE_GRAPH_FILENAME
		movie_categories_path = conf.DATA_DIR + conf.CATEGORY_MOVIES_FILENAME
		output_dir = conf.PART_2_OUTPUT_DIR

		if len(sys.argv) == 3 and sys.argv[2] == "--verbose": verbose = True

	else:
		_print_usage()
		exit(1)

	main(movie_graph_filepath, movie_categories_path, output_dir)
