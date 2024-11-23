import csv, time, os
from datetime import datetime
from collections import namedtuple
from functools import partial
from random import choices, randint, randrange, random
from typing import List, Callable, Tuple

Thing = namedtuple('Thing', ['name', 'rating', 'price'])
Thing3 = namedtuple('Thing3', ['name', 'business_name', 'contact_number', 'email', 'rating', 'price','type'])

# Add Thing2 namedtuple
Thing2 = namedtuple('Thing2', ['name', 'rating', 'price', 'weekend_available'])

base_path = os.path.dirname(__file__)
# Add paths for the second supplier CSV
supplier_list2 = os.path.join(base_path, 'csvs', 'supplier_list2.csv')
csv_file_path3 = os.path.join(base_path, 'csvs', 'supplier_list3.csv')
cake = os.path.join(base_path, 'csvs', 'Cake.csv')
digital_printing = os.path.join(base_path, 'csvs', 'Digital_Printing.csv')
event_planner = os.path.join(base_path, 'csvs', 'Event_Planner.csv')
grazing_table = os.path.join(base_path, 'csvs', 'Grazing_Table.csv')
makeup_and_Hair = os.path.join(base_path, 'csvs', 'Makeup_and_Hair.csv')
photobooth = os.path.join(base_path, 'csvs', 'Photobooth.csv')
photographer = os.path.join(base_path, 'csvs', 'Photographer.csv')

catering = os.path.join(base_path, 'csvs_deluxe', 'Catering.csv')
church = os.path.join(base_path, 'csvs_deluxe', 'Church.csv')
event_stylist = os.path.join(base_path, 'csvs_deluxe', 'Event_Stylist.csv')
events_place = os.path.join(base_path, 'csvs_deluxe', 'Events_Place.csv')
lights_and_sounds = os.path.join(base_path, 'csvs_deluxe', 'Lights_and_Sounds.csv')
user_date_input = time.strftime('%Y-%m-%d')
def read_csv3(file_path, arr):
    with open(file_path, mode='r', newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            thing3 = Thing3(
                name=row['name'],
                business_name=row['business_name'],
                contact_number=row['contact_number'],
                email=row['email'],
                rating=float(row['rating']),
                price=float(row['price']),
                type=row['type']
            )
            arr.append(thing3)

# Function to read supplier_list2.csv and filter based on weekend availability
def read_csv_with_weekend_check(file_path, filtered_arr, skipped_arr, user_date):
    user_date_obj = datetime.strptime(user_date, '%Y-%m-%d')
    is_weekend = user_date_obj.weekday() >= 5  # Saturday (5) or Sunday (6)

    with open(file_path, mode='r', newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            weekend_avail = row['weekend_available'].strip().lower() == 'yes'
            thing2 = Thing2(
                name=row['name'],
                rating=float(row['rating']),
                price=float(row['price']),
                weekend_available=row['weekend_available']
            )
            
            # Include in filtered or skipped based on availability and current date
            if (is_weekend and weekend_avail) or (not is_weekend and not weekend_avail):
                filtered_arr.append(thing2)
            else:
                skipped_arr.append(thing2)

things_list3 = []
filtered_suppliers = []
skipped_suppliers = []

cake_arr = []
digital_printing_arr = []
event_planner_arr = []
grazing_table_arr = []
makeup_and_hair_arr = []
photobooth_arr = []
photographer_arr = []

catering_arr = []
church_arr = []
event_stylist_arr = []
events_place_arr = []
lights_and_sounds_arr = []

def read_csv(file_path, arr):
    with open(file_path, mode='r', newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            thing = Thing(name=row['name'], rating=float(row['rating']), price=float(row['price']))
            arr.append(thing)

read_csv3(csv_file_path3, things_list3)
read_csv(cake , cake_arr)
read_csv(digital_printing , digital_printing_arr)
read_csv(event_planner , event_planner_arr)
read_csv(grazing_table , grazing_table_arr)
read_csv(makeup_and_Hair , makeup_and_hair_arr)
read_csv(photobooth , photobooth_arr)
read_csv(photographer , photographer_arr)

read_csv(catering, catering_arr)
read_csv(church, church_arr)
read_csv(event_stylist, event_stylist_arr)
read_csv(events_place, events_place_arr)
read_csv(lights_and_sounds, lights_and_sounds_arr)
read_csv_with_weekend_check(supplier_list2, filtered_suppliers, skipped_suppliers, user_date_input)

new_things3 = things_list3
cake1 = cake_arr
digital_printing1 = digital_printing_arr
event_planner1 = event_planner_arr
grazing_table1 = grazing_table_arr
makeup_and_hair1 = makeup_and_hair_arr
photobooth1 = photobooth_arr
photographer1 = photographer_arr

catering1 = catering_arr
church1 = church_arr
event_stylist1 = event_stylist_arr
events_place1 = events_place_arr
lights_and_sounds1 = lights_and_sounds_arr

Genome = List[int]
Population = List[Genome]
FitnessFunc = Callable[[Genome], int]
PopulateFunc = Callable[[], Population]
SelectionFunc = Callable[[Population, FitnessFunc], Tuple[Genome, Genome]]
CrossoverFunc = Callable[[Genome, Genome], Tuple[Genome, Genome]]
MutationFunc = Callable[[Genome, int, float], Genome]

category_priorities = {
    'cake': 5,
    'grazing_table': 5,
    'photobooth': 5,
    'digital_printing': 4,
    'photographer': 3,
    'makeup_and_hair': 2,
    'event_planner': 1,
}

sorted_categories = sorted(
    [('cake', cake1), ('grazing_table', grazing_table1), ('photobooth', photobooth1),
     ('digital_printing', digital_printing1), ('photographer', photographer1), ('makeup_and_hair', makeup_and_hair1), ('event_planner', event_planner1),],
    key=lambda x: category_priorities[x[0]],
    reverse=True
)

def generate_genome() -> Genome:
    return [choices([0, 1], k=len(category))[0] for _, category in sorted_categories]

def generate_population(size: int) -> Population:
    return [generate_genome() for _ in range(size)]

def fitness(genome: Genome, price_limit: int) -> int:
    total_price = 0
    total_rating = 0
    
    for (_, category), gene in zip(sorted_categories, genome):
        if gene == 1:
            item = category[0]  # Select the first item in the category
            if total_price + item.price <= price_limit:
                total_price += item.price
                total_rating += item.rating

    if total_price == 0:
        return 1

    price_fitness = total_price / price_limit
    return int(total_rating * (price_fitness ** 2) * 10000) + 1

def selection_pair(population: Population, fitness_func: FitnessFunc) -> Population:
    return choices(
        population=population,
        weights=[fitness_func(genome) for genome in population],
        k=2
    )

def single_point_crossover(a: Genome, b: Genome) -> Tuple[Genome, Genome]:
    if len(a) != len(b):
        raise ValueError("Genomes a and b must be of the same length")

    length = len(a)
    if length < 2:
        return a, b

    p = randint(1, length - 1)
    return a[0:p] + b[p:], b[0:p] + a[p:]

def mutation(genome: Genome, num: int = 1, probability: float = 0.5) -> Genome:
    for _ in range(num):
        index = randrange(len(genome))
        genome[index] = genome[index] if random() > probability else abs(genome[index] - 1)
    return genome

def run_evolution(
        populate_func: PopulateFunc,
        fitness_func: FitnessFunc,
        fitness_limit: int,
        selection_func: SelectionFunc = selection_pair,
        crossover_func: CrossoverFunc = single_point_crossover,
        mutation_func: MutationFunc = mutation,
        generation_limit: int = 2000
) -> Tuple[Genome, int]:
    population = populate_func()
    best_solution = None

    for i in range(generation_limit):
        population = sorted(
            population,
            key=lambda genome: fitness_func(genome),
            reverse=True
        )

        if best_solution is None or fitness_func(population[0]) > fitness_func(best_solution):
            best_solution = population[0]

        if i == generation_limit - 1:
            break

        next_generation = population[0:2]

        for j in range(int(len(population) / 2) - 1):
            parents = selection_func(population, fitness_func)
            offspring_a, offspring_b = crossover_func(parents[0], parents[1])
            offspring_a = mutation_func(offspring_a)
            offspring_b = mutation_func(offspring_b)
            next_generation += [offspring_a, offspring_b]

        population = next_generation

    return best_solution, i + 1

def genome_to_things(genome: Genome, price_limit: int) -> List[Tuple[str, float]]:
    result = []
    total_price = 0
    
    for (_, category), gene in zip(sorted_categories, genome):
        if gene == 1:
            item = category[0]  # Select the first item in the category
            if total_price + item.price <= price_limit:
                total_price += item.price
                result.append((item.name))
    
    return result

# total_price = sum(thing.price for thing in things_list3)
# max_price_limit = 25000  # Set to your desired maximum price
# price_limit = min(total_price, max_price_limit)

# fitness_limit = 1000
# population_size = 20
# generation_limit = 100  

# print(f"Total price of all items: ${total_price:.2f}")
# print(f"Price limit set to: ${price_limit:.2f}")

# start = time.time()
# best_genome, generations = run_evolution(
#     populate_func=partial(generate_population, size=population_size),
#     fitness_func=partial(fitness, price_limit=price_limit),
#     fitness_limit=fitness_limit,
#     generation_limit=generation_limit
# )
# end = time.time()

# print(f"Number of generations: {generations}")
# print(f"Time: {end - start:.2f}s")

# print("Best solution:")
# best_solution = genome_to_things(best_genome, price_limit)
# total_price = 0
# for name in best_solution:
#     print(f"{name}")

# # Debugging output to print skipped suppliers
# print("Skipped Suppliers:")
# for supplier in skipped_suppliers:
#     print(f"{supplier.name} (Set Date Available: {supplier.weekend_available})")


