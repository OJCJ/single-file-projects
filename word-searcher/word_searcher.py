from time import perf_counter
from sys import argv
import os
from unidecode import unidecode

alphabet = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'}

languages = ["danish",
			"english",
			"french",
			"german",
			"italian",
			"norwegian",
			"spanish"]

language = argv[1]


def search(query, language):
	starting_time = perf_counter()
	with open(f"language-files/{language}words.txt", "r") as f:
		word_list = [i.strip() for i in f]
		
		alphabet_index = {}
	
		for inx, word in enumerate(word_list):
			if word[0] not in alphabet_index.keys():
				alphabet_index[word[0]] = inx
	
		query = query.lower()

		for c in query:
			if c not in alphabet:
				print(f"\nInvalid character '{c}'. Please use only unaccented latin letters.", end="")
				return []
	
		results = []
		
		for word in word_list[alphabet_index[query[0]]:-1]:
			word_no_accent = unidecode(word)
			#print(word_no_accent)
			if word_no_accent[:len(query)] == query:
				results.append(word)
	
			if word_no_accent[:len(query)] > query:
				break
		
		ending_time = perf_counter()
		print(f"Time taken: {(ending_time - starting_time)*1000}ms")

		return results

def clear_console():
	command = 'clear'
	if os.name in ('nt', 'dos'):
		command = 'cls'
	os.system(command)

def main():
	if language not in languages:
		print("Invalid language. Please try again with one of these:")
		for i in languages:
			print(f"- {i}")
		return

	search_query = input(f"Search: ")

	clear_console()

	while True:

		print(f"Results for search: '{search_query}'")

		if search_query != "":
			for inx, val in enumerate(search(search_query, language)):
				print_end = "" + "\n"*((inx+1)%3 == 0)
				print(f"{'| '*(inx%3 == 0)}{val} | ", end=print_end)

		print("\n")

		search_query = input(f"Search: ")

		clear_console()

if __name__ == "__main__":
	main()