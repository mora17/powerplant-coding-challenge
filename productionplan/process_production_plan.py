# Calculate production from the given params
def calculate_production_plan(load, fuels, powerplants):
    possible_solutions = []

    wind_cost = 0.0
    gas_cost = fuels['gas(euro/MWh)']
    kerosine_cost = fuels['kerosine(euro/MWh)']
    wind_percentage = fuels['wind(%)']

    grouped_plants = _group_powerplants_by_type(powerplants)
    sorted_plant_types = _sort_plant_types_by_cost(wind_cost, gas_cost, kerosine_cost)
    _find_solutions(possible_solutions, [], load, grouped_plants, wind_percentage, sorted_plant_types)

    if not possible_solutions:
        raise ValueError("No valid production plan found")

    return format_solution(powerplants, possible_solutions[0])

# Group powerplants by their type
def _group_powerplants_by_type(powerplants):
    grouped_plants = {'windturbine': [], 'gasfired': [], 'turbojet': []}
    for powerplant in powerplants:
        grouped_plants[powerplant['type']].append(powerplant)
    return grouped_plants

# Use merit-order to set the order of plants to be used first
def _sort_plant_types_by_cost(wind_cost, gas_cost, kerosine_cost):
    plant_costs = {'windturbine': wind_cost, 'gasfired': gas_cost, 'turbojet': kerosine_cost}
    return sorted(plant_costs.keys(), key=lambda plant_type: plant_costs[plant_type])

# Find the best plant based on pmax and efficiency
def _find_plant(plants, desired_load):
    return sorted(plants, key=lambda plant: (-plant['pmax'], -plant['efficiency'], plant['name']))[0]

# Calculate power for the plant
def _power_for(plant, desired_load, wind_percentage):
    if desired_load < plant['pmin']:
        return plant['pmin']

    if plant['type'] == 'windturbine':
        max_power = (plant['pmax'] * wind_percentage) / 100.0
    else:
        max_power = plant['pmax']

    return min(max_power, desired_load)

# Adjust power from current combination
def _adjust_power_from(current_combination, power_difference):
    for plant in reversed(current_combination):
        adjusted_power = plant['selected_power'] - power_difference
        if adjusted_power >= plant['pmin']:
            plant['selected_power'] -= power_difference
            return

# Find possible solutions
def _find_solutions(possible_solutions, current_combination, desired_load, grouped_plants, wind_percentage, sorted_plant_types):
    if desired_load <= 0:
        possible_solutions.append(current_combination.copy())
        return

    plant = None
    for plant_type in sorted_plant_types:
        if plant_type == 'windturbine' and wind_percentage == 0:
            continue  # Skip wind turbines if wind percentage is zero

        if grouped_plants[plant_type]:
            plant = _find_plant(grouped_plants[plant_type], desired_load)
            break

    if not plant:
        return

    # Choose the necessary power for the plant
    selected_power = _power_for(plant, desired_load, wind_percentage)
    if desired_load < selected_power:
        _adjust_power_from(current_combination, selected_power - desired_load)
    plant['selected_power'] = selected_power
    load_left = desired_load - selected_power

    current_combination.append(plant)

    next_grouped_plants = {ptype: [p for p in plants if p != plant] for ptype, plants in grouped_plants.items()}

    _find_solutions(possible_solutions, current_combination, load_left, next_grouped_plants, wind_percentage, sorted_plant_types)

    current_combination.remove(plant)

# Format solution as requested by requirements
def format_solution(powerplants, solution):
    power_dict = {item['name']: item['selected_power'] for item in solution}
    return [{'name': plant['name'], 'p': power_dict.get(plant['name'], 0.0)} for plant in powerplants]
