import itertools
import logging
import os
import random
import string
import sys
from datetime import datetime, timedelta

logger = logging.getLogger("null")
logger.addHandler(logging.NullHandler())

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

processed_file = os.path.join(DATA_DIR, 'processed.txt')
words_file = os.path.join(DATA_DIR, 'us_words.txt')
cities_file = os.path.join(DATA_DIR, 'us_cities.txt')
firstnames_file = os.path.join(DATA_DIR, 'firstnames.txt')
lastnames_file = os.path.join(DATA_DIR, 'lastnames.txt')
dupes_file = os.path.join(DATA_DIR, 'dupes.txt')
invalids_file = os.path.join(DATA_DIR, 'invalids.txt')

special_char_types = r"""!@#$%&*^?_~"()[]{}|\/`<>:;,+-./='"""
special_char_weights = [50, 40, 30, 20, 10, 8, 6, 5, 4, 3] + [2] * (len(special_char_types) - 10)
valid_chars = (string.ascii_lowercase + string.ascii_uppercase + string.digits + special_char_types)
processed_count = 0
total_generated = 0
total_characters = 0

swap_mapper = {
    'a': '@',
    'b': ['6', '8'],
	'c': ['<', '{', '[', '('],
    'e': '3',
	'g': ['6', '9', 'q'],
    'i': ['!', '1', '|', 'l'],
	'l': ['I', '1', '|'],
    'o': '0',
	'q': ['0', 'O', 'g'],
    's': ['$', '5'],
    't': '7',
	'x': ['%', '*'],
	'z': '2'
}

def load_file(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file.readlines()]

def get_swapped_char(char, case_choice = 'lower'):
    global swap_mapper
    lower_char = char.lower()
    if lower_char in swap_mapper:
        mapping = swap_mapper[lower_char]
        if isinstance(mapping, list):
            return random.choice(mapping)
        return mapping
    if case_choice == 'upper':
        return char.upper()
    return char.lower()

def apply_random_case_and_swap(word):
    result = []
    case_choice = random.choices(['lower', 'upper', 'title', 'random', 'swap', 'hybrid', 'misspell'],weights=[10, 5, 3, 2, 2, 1, 1], k=1)[0]
    if case_choice == 'lower':
        result.append(word.lower())
    elif case_choice == 'upper':
        result.append(word.upper())
    elif case_choice == 'title':
        result.append(word.capitalize())
    elif case_choice == 'random':
        for char in word:
            result.append(char.upper() if random.random() > 0.8 else char.lower())
    elif case_choice == 'hybrid':
        for i, char in enumerate(word):
            if len(word) <= 3:
                result.append(char.lower()) if i % 2 != 0 else result.append(char.upper())
            else:
                result.append(char.upper() if random.random() > 0.5 else char.lower())
    elif case_choice == 'swap':
        remaining_case_choice = random.choices(['lower', 'upper'], weights=[4, 1], k=1)[0]
        random_guess = random.random()
        for i, char in enumerate(word):
            if i == 0 and random_guess < 0.1:
                result.append(char.upper())
            elif random_guess < 0.30:
                result.append(get_swapped_char(char, remaining_case_choice))
            else:
                if remaining_case_choice == 'lower':
                    result.append(char.lower())
                elif remaining_case_choice == 'upper':
                    result.append(char.upper())
    elif case_choice == 'misspell':
        for char in word:
            rand_val = random.random()
            if char in 'aeiou' and rand_val > 0.8:
                result.append(char * 2)
            elif rand_val > 0.9:
                result.append(char * 2)
            else:
                result.append(char)
    return ''.join(result)

def generate_password(char_count, order, seed, selected_special_chars):
    char_pool = ''
    for char_type in order:
        if char_type == 'digits':
            char_pool += '0123456789'
        elif char_type == 'uppercase':
            char_pool += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        elif char_type == 'lowercase':
            char_pool += 'abcdefghijklmnopqrstuvwxyz'
        elif char_type == 'special' and selected_special_chars:
            char_pool += selected_special_chars
    rng = random.Random(seed)
    password = ''.join(rng.choice(char_pool) for _ in range(char_count))
    return password

def random_datetime(start_year, end_year):
    start_date = datetime(start_year, 1, 1, 0, 0)
    end_date = datetime(end_year, 12, 31, 23, 59)
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    random_seconds = random.randint(0, 24 * 3600 - 1)
    return start_date + timedelta(days=random_days, seconds=random_seconds)

def total_password_length(password_parts):
    return sum(len(part) for part in password_parts)

def generate_existing_files():
    global logger, processed_file, dupes_file, invalids_file
    if not os.path.exists(dupes_file):
        with open(dupes_file, 'w') as file:
            file.write("")
        logger.info(f"File '{dupes_file}' created successfully.")
    if not os.path.exists(processed_file):
        with open(processed_file, 'w') as file:
            file.write("")
        logger.info(f"File '{processed_file}' created successfully.")
    if not os.path.exists(invalids_file):
        with open(invalids_file, 'w') as file:
            file.write("")
        logger.info(f"File '{invalids_file}' created successfully.")

def process_cleanup():
    global logger, valid_chars, processed_file, dupes_file, invalids_file
    logger.info("process_cleanup...")
    with open(processed_file, 'r', encoding='utf-8') as file:
        words = [word.strip() for word in file.readlines()]
    unique_words = set()
    duplicates = set()
    invalid_words = set()
    print("Starting cleaning...")
    logger.info("Starting cleaning...")
    for word in words:
        valid_word = ''.join([char for char in word if char in valid_chars])
        if valid_word != word:
            invalid_words.add(word)
        if valid_word:
            if valid_word in unique_words:
                duplicates.add(valid_word)
            else:
                unique_words.add(valid_word)
    logger.info("Sorting unique_words...")
    unique_words = sorted(unique_words)
    logger.info("Sorting duplicates...")
    duplicates = sorted(duplicates)
    logger.info("Sorting invalid_words...")
    invalid_words = sorted(invalid_words)
    with open(processed_file, 'w', encoding='utf-8') as file:
        file.write('\n'.join(unique_words))
    logger.info(f"processed written to {processed_file}")
    with open(dupes_file, 'a', encoding='utf-8') as file:
        file.write('\n'.join(duplicates))
    logger.info(f"processed_dupes written to {dupes_file}")
    with open(invalids_file, 'a', encoding='utf-8') as file:
        file.write('\n'.join(invalid_words))
    logger.info(f"invalids_file written to {invalids_file}")

def run_passgen(pass_type='WORD', process_amount=1000000, log=None):
    global logger
    logger = log
    global  processed_count, total_generated, total_characters, special_char_types, words_file, cities_file, lastnames_file, firstnames_file, special_char_weights
    logger.info(f"Starting BTC passgen task for pass_type: ({pass_type})  process_amount: ({process_amount}) ")
    generate_existing_files()
    if pass_type == 'SEED':
        logger.info(f"Running seeds...")
        with open(processed_file, 'a') as file:
            while True:
                if processed_count >= process_amount:
                    break
                random_date = random_datetime(2009, 2015)
                seed = random_date.strftime('%m%d%Y%H%M%S')
                char_count = random.randint(15, 45)
                while True:
                    use_numbers = random.random() < 0.91
                    use_lowercase = random.random() < 0.87
                    use_uppercase = random.random() < 0.93
                    use_special = random.random() < 0.15
                    if use_numbers and (use_lowercase or use_uppercase):
                        break
                selected_char_types = []
                selected_special_chars = None
                if use_numbers:
                    selected_char_types.append('digits')
                if use_lowercase:
                    selected_char_types.append('lowercase')
                if use_uppercase:
                    selected_char_types.append('uppercase')
                if use_special:
                    selected_char_types.append('special')
                    selected_special_chars = special_char_types
                    # selected_special_chars = ''.join(sorted(random.sample(mg.special_char_types, 5), key=lambda x: mg.special_char_types.index(x)))

                all_permutations = list(itertools.permutations(selected_char_types))
                string_date = str(seed)
                int_date = int(seed)
                string_char_date = str(char_count) + str(seed)
                int_char_date = int(str(char_count) + str(seed))
                string_date_char = str(seed) + str(char_count)
                int_date_char = int(str(seed) + str(char_count))
                seed_list = []
                for i, order in enumerate(all_permutations):
                    password1 = generate_password(char_count=char_count, order=order, seed=string_date, selected_special_chars=selected_special_chars)
                    password2 = generate_password(char_count=char_count, order=order, seed=int_date, selected_special_chars=selected_special_chars)
                    password3 = generate_password(char_count=char_count, order=order, seed=string_char_date, selected_special_chars=selected_special_chars)
                    password4 = generate_password(char_count=char_count, order=order, seed=int_char_date, selected_special_chars=selected_special_chars)
                    password5 = generate_password(char_count=char_count, order=order, seed=string_date_char, selected_special_chars=selected_special_chars)
                    password6 = generate_password(char_count=char_count, order=order, seed=int_date_char, selected_special_chars=selected_special_chars)
                    seed_list.extend([password1, password2, password3, password4, password5, password6])
                    total_generated += 6
                file.write("\n".join(seed_list) + "\n")
                processed_count += 1
                if processed_count % 100 == 0:
                    sys.stdout.write(f"\rProcessed count: {processed_count}")
                    sys.stdout.flush()
        logger.info(f"\nProcessing complete total SEEDS: {total_generated}")
    if pass_type == 'WORD':
        logger.info(f"Running words...")
        first_names = load_file(firstnames_file)
        last_names = load_file(lastnames_file)
        cities = load_file(cities_file)
        words = load_file(words_file)
        with open(processed_file, 'a') as file:
            while True:
                if processed_count >= process_amount:
                    break
                password_parts = []
                digit_part_count = 0
                non_digit_added = False
                part_generators = [
                    lambda: apply_random_case_and_swap(random.choice(first_names)),
                    lambda: apply_random_case_and_swap(random.choice(last_names)),
                    lambda: apply_random_case_and_swap(random.choice(words)),
                    lambda: apply_random_case_and_swap(random.choice(cities)),
                ]
                password_min_size = 15
                password_stop_size = 17
                password_max_size = 24
                password_part_min = 3
                digit_part_max = 2
                digit_part_chance = 0.40
                word_part_chance = 0.17
                while len(password_parts) < password_part_min or total_password_length(password_parts) <= password_min_size:
                    shuffled_part_generators = random.choices(part_generators, weights=[1, 1, 2, 0.5], k=len(part_generators))
                    random.shuffle(shuffled_part_generators)
                    if (non_digit_added and digit_part_count < digit_part_max) or len(password_parts) == 0:
                        if random.random() < digit_part_chance:
                            num_digits = random.choices([1, 2, 3, 4], weights=[4, 3, 2, 1])[0]
                            password_parts.append(''.join(random.choices('0123456789', k=num_digits)))
                            digit_part_count += 1
                    if len(password_parts) >= password_part_min and total_password_length(password_parts) >= password_stop_size:
                        break
                    for generator in shuffled_part_generators:
                        if random.random() < word_part_chance:
                            current_length = total_password_length(password_parts)
                            new_part = generator()
                            if current_length + len(new_part) < password_max_size:
                                password_parts.append(new_part)
                                non_digit_added = True
                        if len(password_parts) >= password_part_min and total_password_length(password_parts) >= password_stop_size:
                            break
                    if len(password_parts) >= password_part_min and total_password_length(password_parts) >= password_stop_size:
                        break
                all_permutations = list(itertools.permutations(password_parts))
                permutated_passwords = []
                for i, order in enumerate(all_permutations):
                    special_char_chance = 0.35
                    use_special_chars = random.random()
                    pass_pool = ''
                    for idx, pass_part in enumerate(order):
                        chosen_position = random.choices(['beginning', 'middle', 'end'], weights=[5, 1, 7], k=1)[0]
                        if idx == 0 and chosen_position == 'beginning':
                            insert_special = True
                        elif idx == len(order) - 1 and chosen_position == 'end':
                            insert_special = True
                        elif idx != 0 and idx != len(order) - 1 and chosen_position == 'middle':
                            insert_special = True
                        else:
                            insert_special = False
                        if insert_special and use_special_chars < special_char_chance:
                            num_specials = random.choices([1, 2], weights=[7, 1])[0]
                            special_chars = ''.join(random.choices(special_char_types, weights=special_char_weights, k=num_specials))
                            random_spot = random.random()
                            if idx == 0:
                                pass_pool += special_chars + pass_part
                                special_char_chance *= 0.7
                            elif idx == len(order) - 1:
                                pass_pool += pass_part + special_chars
                                special_char_chance *= 0.7
                            elif random_spot < 0.15:
                                pass_pool += special_chars + pass_part
                                special_char_chance *= 0.7
                            elif random_spot > 0.85:
                                pass_pool += pass_part + special_chars
                                special_char_chance *= 0.7
                            else:
                                pass_pool += pass_part
                        else:
                            pass_pool += pass_part
                    permutated_passwords.append(pass_pool)
                    total_generated += 1
                    total_characters += len(pass_pool)
                file.write('\n'.join(permutated_passwords) + '\n')
                processed_count += 1
                if processed_count % 100 == 0:
                    sys.stdout.write(f"\rProcessed count: {processed_count}")
                    sys.stdout.flush()
        logger.info(f"\nProcessing complete total WORDS: {total_generated}")
        logger.info(f"Cumulative average length: {total_characters / total_generated:.2f}")
    process_cleanup()
