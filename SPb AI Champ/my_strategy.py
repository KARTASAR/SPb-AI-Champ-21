from model import *
import math

all_resources = [Resource.METAL, Resource.STONE, Resource.ORE,
                 Resource.SAND, Resource.ACCUMULATOR, Resource.ORGANICS,
                 Resource.CHIP, Resource.SILICON, Resource.PLASTIC]

types_of_planets = ['stone', 'metal', 'ore', 'sand',
                    'chip', 'accumulator', 'organics', 'silicon', 'plastic', 'replicator']

def distance(position1, position2):
    return abs(position1[0] - position2[0]) + abs(position1[1] - position2[1])
                
class this_planet:
    def __init__(self, planet: Planet, idx: int, my_index):
        self.idx = idx
        self.planet = planet
        self.x = planet.x
        self.y = planet.y
        self.harvestable_resource = planet.harvestable_resource
        self.my_workers = 0
        self.enemies_on_planet = 0
        self.my_index = my_index
        self.workers_in_flight = 0
        self.game = None
        self.building = planet.building
        self.resources_in_flight = {res: 0 for res in all_resources} 
        self.workers_in_flight = 0
        self.resources = {res: 0 for res in all_resources}
        self.count_workers()
    
    def count_workers(self):
        self.my_workers, self.enemies_on_planet = 0, 0
        for work_gr in self.planet.worker_groups:
            if work_gr.player_index == self.my_index:
                self.my_workers += work_gr.number
            else:
                self.enemies_on_planet += work_gr.number
    
    def refresh(self, planet):
        self.resources_in_flight = {res: 0 for res in all_resources}
        self.resources = {res: 0 for res in all_resources}
        for res, amount in planet.resources.items(): self.resources[res] += amount
        self.workers_in_flight = 0
        self.planet = planet
        self.building = planet.building
        self.count_workers()
        

class MyStrategy:
    def __init__(self):
        self.planets = {}
        self.special_planets = {'stone': [], 'sand': [], 'ore': [], 'organics': [], 'free': []}
        self.starter_planet_idx = 0
        self.starting_planet = None
        # Сначала добавим все возможно полезные планеты в special planets, 
        # затем проводим отбор и распределяем планеты по my_planets
        self.my_planets = {'stone': 0, 'ore': None, 'sand': None, 'organics': None, 
                            'furnace': None, 'foundry': None, 'bioreactor': None,
                            'chip': None, 'accumulator': None, 'replicator': None}
        self.list_of_my_planets = []
        self.moves = []
        self.game = None
        self.need_resources_for_building = {}
        self.planets_resources = {}
        self.delayed_moves = {}
    
    def find_closest_planet(self, start_planet):
        closest_distance, close_planet = 10000, None 
        for idx, planet in self.planets.items():
            if planet not in self.list_of_my_planets:
                dist = distance([start_planet.x, start_planet.y], [planet.x, planet.y])
                if dist < closest_distance:
                    closest_distance = dist
                    close_planet = planet
        self.list_of_my_planets.append(close_planet)
        return close_planet


    def starting(self):
        for idx, planet in enumerate(self.game.planets):
            self.planets[idx] = this_planet(planet, idx, self.game.my_index)
            if self.planets[idx].my_workers > 0:
                self.special_planets['stone'] = idx 
                self.starter_planet_idx = idx
                self.starting_planet = self.planets[idx]
            
        for idx, planet in self.planets.items():
            if planet.harvestable_resource in all_resources and idx != self.starter_planet_idx:
                if planet.harvestable_resource == Resource.SAND:
                    self.special_planets['sand'].append(planet)
                if planet.harvestable_resource == Resource.ORE:
                    self.special_planets['ore'].append(planet)
                if planet.harvestable_resource == Resource.ORGANICS:
                    self.special_planets['organics'].append(planet)
    
    def organising_planets(self):
        closest_sand_distance = 10000
        closest_ore_distance = 10000
        closest_organics_distance = 10000

        closest_sand_planet = None
        closest_ore_planet = None
        closest_organics_planet = None

        for res, list_of_planets in self.special_planets.items():
            if res == 'stone':
                continue

            if res == 'sand':
                for planet in list_of_planets:
                    if distance([self.starting_planet.x, self.starting_planet.y], [planet.x, planet.y]) < closest_sand_distance:
                        closest_sand_distance = distance([self.starting_planet.x, self.starting_planet.y], [planet.x, planet.y])
                        closest_sand_planet = planet
            elif res == 'ore':
                for planet in list_of_planets:
                    if distance([self.starting_planet.x, self.starting_planet.y], [planet.x, planet.y]) < closest_ore_distance:
                        closest_ore_distance = distance([self.starting_planet.x, self.starting_planet.y], [planet.x, planet.y])
                        closest_ore_planet = planet
            elif res == 'organics':
                for planet in list_of_planets:
                    if distance([self.starting_planet.x, self.starting_planet.y], [planet.x, planet.y]) < closest_organics_distance:
                        closest_organics_distance = distance([self.starting_planet.x, self.starting_planet.y], [planet.x, planet.y])
                        closest_organics_planet = planet
        
        self.my_planets['stone'] = self.starting_planet
        self.my_planets['sand'] = closest_sand_planet
        self.my_planets['ore'] = closest_ore_planet
        self.my_planets['organics'] = closest_organics_planet

        self.list_of_my_planets.append(self.starting_planet)
        self.list_of_my_planets.append(closest_sand_planet)
        self.list_of_my_planets.append(closest_ore_planet)
        self.list_of_my_planets.append(closest_organics_planet)

        self.my_planets['furnace'] = self.find_closest_planet(self.my_planets['sand'])
        self.list_of_my_planets.append(self.my_planets['furnace'])
        self.my_planets['foundry'] = self.find_closest_planet(self.my_planets['ore'])
        self.list_of_my_planets.append(self.my_planets['foundry'])
        self.my_planets['bioreactor'] = self.find_closest_planet(self.my_planets['organics'])
        self.list_of_my_planets.append(self.my_planets['bioreactor'])

        self.my_planets['chip'] = self.find_closest_planet(self.my_planets['furnace'])
        self.list_of_my_planets.append(self.my_planets['chip'])
        self.my_planets['accumulator'] = self.find_closest_planet(self.my_planets['foundry'])
        self.list_of_my_planets.append(self.my_planets['accumulator'])

        self.my_planets['replicator'] = self.find_closest_planet(self.my_planets['chip'])
        self.list_of_my_planets.append(self.my_planets['replicator'])
    
    def updating(self):
        
        for idx, planet in enumerate(self.game.planets): 
            self.planets[idx].refresh(planet)

        updated_planet_list = []
        
        for type, planet in self.my_planets.items():
            if type == 'stone':
                continue
            self.my_planets[type] = self.planets[planet.idx]
            updated_planet_list.append(self.planets[planet.idx])
        self.list_of_my_planets = updated_planet_list
            
        self.need_resources_for_building = {}
        self.planets_resources = {}

    def get_action(self, game: Game) -> Action:
        moves, builds = [], []
        self.game = game

        if game.current_tick == 0: 
            self.starting()
            self.organising_planets()
        else: 
            self.updating()

        for type, planet in self.my_planets.items():
            idx = planet.idx
            stone_planet = self.starting_planet
            ore_planet = self.my_planets['ore']
            sand_planet = self.my_planets['sand']
            organics_planet = self.my_planets['organics']
            metal_planet = self.my_planets['foundry']
            plastic_planet = self.my_planets['bioreactor']
            silicon_planet = self.my_planets['furnace']
            accumulator_planet = self.my_planets['accumulator']
            chip_planet = self.my_planets['chip']
            replicator_planet = self.my_planets['replicator']

            if type == 'stone': 
                if planet.my_workers > game.max_builders or Resource.STONE in planet.resources:
                        if ore_planet.my_workers + ore_planet.workers_in_flight < 150 and ore_planet.planet.building is None:
                            moves.append(MoveAction(idx, ore_planet.idx, 100, Resource.STONE))
                        elif sand_planet.my_workers + sand_planet.workers_in_flight < 150 and sand_planet.planet.building is None:
                            moves.append(MoveAction(idx, sand_planet.idx, 100, Resource.STONE))
                        elif organics_planet.my_workers + organics_planet.workers_in_flight < 150 and organics_planet.planet.building is None:
                            moves.append(MoveAction(idx, organics_planet.idx, 100, Resource.STONE))
                        elif metal_planet.my_workers + metal_planet.workers_in_flight < 100 and metal_planet.planet.building is None:
                            moves.append(MoveAction(idx, metal_planet.idx, 100, Resource.STONE))
                        elif plastic_planet.my_workers + plastic_planet.workers_in_flight < 100 and plastic_planet.planet.building is None:
                            moves.append(MoveAction(idx, plastic_planet.idx, 100, Resource.STONE))
                        elif silicon_planet.my_workers + silicon_planet.workers_in_flight < 100 and silicon_planet.planet.building is None:
                            moves.append(MoveAction(idx, silicon_planet.idx, 100, Resource.STONE))
                        elif accumulator_planet.my_workers + accumulator_planet.workers_in_flight < 100 and accumulator_planet.planet.building is None:
                            moves.append(MoveAction(idx, accumulator_planet.idx, 100, Resource.STONE))
                        elif chip_planet.my_workers + chip_planet.workers_in_flight < 100 and chip_planet.planet.building is None:
                            moves.append(MoveAction(idx, chip_planet.idx, 100, Resource.STONE))
                        elif replicator_planet.my_workers + replicator_planet.workers_in_flight < 200 and replicator_planet.planet.building is None:
                            moves.append(MoveAction(idx, replicator_planet.idx, 100, Resource.STONE))
                        else:
                            moves.append(MoveAction(idx, ore_planet.idx, 50, None))
            
            elif type == 'ore':
                    if planet.planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.MINES))
                    elif Resource.ORE in planet.planet.resources and planet.planet.resources[Resource.ORE] > 100:
                        num_workers_to_send = min(planet.my_workers, 100)
                        moves.append(MoveAction(idx, metal_planet.idx, num_workers_to_send, Resource.ORE))
                    elif planet.workers_in_flight == 0 and planet.planet.building is None:
                        moves.append(MoveAction(idx, stone_planet.idx, planet.my_workers, None))

            elif type == 'sand':
                    if planet.planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.CAREER))
                    elif Resource.SAND in planet.planet.resources and planet.planet.resources[Resource.SAND] >= 100:
                        num_workers_to_send = min(planet.my_workers, 100)
                        moves.append(MoveAction(idx, silicon_planet.idx, num_workers_to_send, Resource.SAND))
                    elif planet.workers_in_flight == 0 and planet.planet.building is None:
                        moves.append(MoveAction(idx, stone_planet.idx, planet.my_workers, None))

            elif type == 'organics':
                    if planet.planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.FARM))
                    elif Resource.ORGANICS in planet.planet.resources and planet.planet.resources[Resource.ORGANICS] >= 100:
                        num_workers_to_send = min(planet.planet.resources[Resource.ORGANICS], 100)
                        moves.append(MoveAction(idx, plastic_planet.idx, num_workers_to_send, Resource.ORGANICS))
                    elif planet.workers_in_flight == 0 and planet.planet.building is None:
                        moves.append(MoveAction(idx, stone_planet.idx, planet.my_workers, None))

            elif type == 'foundry':
                    need_ore = Resource.ORE not in planet.planet.resources or planet.planet.resources[Resource.ORE] == 1
                    if planet.my_workers and planet.planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.FOUNDRY))
                    elif (Resource.METAL in planet.planet.resources and planet.planet.resources[Resource.METAL] > 5) and (need_ore or planet.planet.resources[Resource.METAL] > 200):
                        num_workers_to_send = min(planet.my_workers, planet.planet.resources[Resource.METAL], 150)
                        if Resource.METAL in replicator_planet.planet.resources and replicator_planet.planet.resources[Resource.METAL] > 100:
                            moves.append(MoveAction(idx, accumulator_planet.idx, num_workers_to_send // 2, Resource.METAL))
                            moves.append(MoveAction(idx, chip_planet.idx, num_workers_to_send // 2, Resource.METAL))
                        else:
                            moves.append(MoveAction(idx, accumulator_planet.idx, num_workers_to_send // 3, Resource.METAL))
                            moves.append(MoveAction(idx, chip_planet.idx, num_workers_to_send // 3, Resource.METAL))
                            moves.append(MoveAction(idx, replicator_planet.idx, num_workers_to_send // 3, Resource.METAL))
                    elif planet.my_workers > 0 and (Resource.ORE not in planet.planet.resources or planet.planet.resources[Resource.ORE] == 1):
                        moves.append(MoveAction(idx, ore_planet.idx, planet.my_workers, None))
                    if (planet.planet.building is None and planet.my_workers >= 100) or replicator_planet.planet.building is None:
                        moves.append(MoveAction(idx, stone_planet.idx, planet.my_workers, None))

            elif type == 'furnace':
                    if planet.planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.FURNACE))
                    elif Resource.SILICON in planet.planet.resources and (Resource.SAND not in planet.planet.resources or planet.planet.resources[Resource.SAND] == 1):
                        num_workers_to_send = min(planet.my_workers, planet.planet.resources[Resource.SILICON], 50)
                        moves.append(MoveAction(idx, chip_planet.idx, num_workers_to_send, Resource.SILICON))
                    elif Resource.SAND not in planet.planet.resources or planet.planet.resources[Resource.SAND] == 1:
                        moves.append(MoveAction(idx, sand_planet.idx, planet.my_workers, None))
                    if planet.planet.building is None and planet.my_workers >= 100:
                        moves.append(MoveAction(idx, stone_planet.idx, planet.my_workers, None))

            elif type == 'bioreactor':
                    need_organics = Resource.ORGANICS not in planet.planet.resources or planet.planet.resources[Resource.ORGANICS] == 1
                    if planet.planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.BIOREACTOR))
                    elif Resource.PLASTIC in planet.planet.resources and need_organics:
                        num_workers_to_send = min(planet.my_workers, planet.planet.resources[Resource.PLASTIC], 50)
                        moves.append(MoveAction(idx, accumulator_planet.idx, num_workers_to_send, Resource.PLASTIC))
                    elif need_organics:
                        moves.append(MoveAction(idx, organics_planet.idx, planet.my_workers, None))

                    if planet.planet.building is None and planet.my_workers >= 100:
                        moves.append(MoveAction(idx, stone_planet.idx, planet.my_workers, None))

            elif type == 'accumulator':
                    need_plastic = Resource.PLASTIC not in planet.planet.resources or planet.planet.resources[Resource.PLASTIC] == 1
                    need_metal = Resource.METAL not in planet.planet.resources or planet.planet.resources[Resource.METAL] == 1
                    if planet.planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.ACCUMULATOR_FACTORY))
                    elif Resource.ACCUMULATOR in planet.planet.resources and (need_plastic or need_metal):
                        num_workers_to_send = min(planet.my_workers, planet.planet.resources[Resource.ACCUMULATOR], 50)
                        moves.append(MoveAction(idx, replicator_planet.idx, num_workers_to_send, Resource.ACCUMULATOR))
                    elif need_plastic and need_metal:
                        moves.append(MoveAction(idx, plastic_planet.idx, planet.my_workers//2, None))
                        moves.append(MoveAction(idx, metal_planet.idx, planet.my_workers//2, None))
                    elif need_plastic:
                        moves.append(MoveAction(idx, plastic_planet.idx, planet.my_workers, None))
                    elif need_metal:
                        moves.append(MoveAction(idx, metal_planet.idx, planet.my_workers, None))

            elif type == 'chip':
                    need_silicon = Resource.SILICON not in planet.planet.resources or planet.planet.resources[Resource.SILICON] == 1
                    need_metal = Resource.METAL not in planet.planet.resources or planet.planet.resources[Resource.METAL] == 1
                    if planet.planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.CHIP_FACTORY))
                    elif Resource.CHIP in planet.planet.resources and (need_silicon or need_metal):
                        num_workers_to_send = min(planet.my_workers, planet.planet.resources[Resource.CHIP], 50)
                        moves.append(MoveAction(idx, replicator_planet.idx, num_workers_to_send, Resource.CHIP))
                    elif need_silicon and need_metal:
                        moves.append(MoveAction(idx, silicon_planet.idx, planet.my_workers // 2, None))
                        moves.append(MoveAction(idx, metal_planet.idx, planet.my_workers // 2, None))
                    elif need_silicon:
                        moves.append(MoveAction(idx, silicon_planet.idx, min(planet.my_workers, 50), None))
                    elif need_metal:
                        moves.append(MoveAction(idx, metal_planet.idx, min(planet.my_workers, 50), None))

                    if planet.planet.building is None and planet.my_workers >= 200:
                        moves.append(MoveAction(idx, stone_planet.idx, planet.my_workers, None))

            elif type == 'replicator':
                    need_chip = Resource.CHIP not in planet.planet.resources or planet.planet.resources[Resource.CHIP] == 1
                    need_metal = Resource.METAL not in planet.planet.resources or planet.planet.resources[Resource.METAL] == 1
                    need_accumulator = Resource.ACCUMULATOR not in planet.planet.resources or planet.planet.resources[Resource.ACCUMULATOR] == 1
                    if planet.planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.REPLICATOR))
                    elif need_chip or need_metal or need_accumulator:
                        if Resource.ACCUMULATOR in planet.planet.resources and planet.planet.resources[Resource.ACCUMULATOR] > 100:
                            moves.append(MoveAction(idx, sand_planet.idx, planet.my_workers // 2, None))
                            moves.append(MoveAction(idx, ore_planet.idx, planet.my_workers // 2, None))
                        else:
                            moves.append(MoveAction(idx, organics_planet.idx, planet.my_workers // 3, None))
                            moves.append(MoveAction(idx, sand_planet.idx, planet.my_workers // 3, None))
                            moves.append(MoveAction(idx, ore_planet.idx, planet.my_workers // 3, None))
                

        return Action(moves, builds, Specialty.PRODUCTION)