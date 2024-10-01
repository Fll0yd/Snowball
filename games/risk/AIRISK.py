import random
import time

class RiskGame:
    def __init__(self, player_territories):
        self.players = list(player_territories.keys())
        self.trade_in_count = 0
        self.territories = {
            'Alaska': {'owner': None, 'troops': 0},
            'Alberta': {'owner': None, 'troops': 0},
            'Argentina': {'owner': None, 'troops': 0},
            'Brazil': {'owner': None, 'troops': 0},
            'Central America': {'owner': None, 'troops': 0},
            'China': {'owner': None, 'troops': 0},
            'Congo': {'owner': None, 'troops': 0},
            'East Africa': {'owner': None, 'troops': 0},
            'Eastern Australia': {'owner': None, 'troops': 0},
            'Eastern United States': {'owner': None, 'troops': 0},
            'Egypt': {'owner': None, 'troops': 0},
            'Great Britain': {'owner': None, 'troops': 0},
            'Greenland': {'owner': None, 'troops': 0},
            'Iceland': {'owner': None, 'troops': 0},
            'India': {'owner': None, 'troops': 0},
            'Indonesia': {'owner': None, 'troops': 0},
            'Irkutsk': {'owner': None, 'troops': 0},
            'Japan': {'owner': None, 'troops': 0},
            'Kamchatka': {'owner': None, 'troops': 0},
            'Madagascar': {'owner': None, 'troops': 0},
            'Middle East': {'owner': None, 'troops': 0},
            'Mongolia': {'owner': None, 'troops': 0},
            'New Guinea': {'owner': None, 'troops': 0},
            'North Africa': {'owner': None, 'troops': 0},
            'Northern Europe': {'owner': None, 'troops': 0},
            'Northwest Territory': {'owner': None, 'troops': 0},
            'Ontario': {'owner': None, 'troops': 0},
            'Peru': {'owner': None, 'troops': 0},
            'Quebec': {'owner': None, 'troops': 0},
            'Scandinavia': {'owner': None, 'troops': 0},
            'Siam': {'owner': None, 'troops': 0},
            'Siberia': {'owner': None, 'troops': 0},
            'South Africa': {'owner': None, 'troops': 0},
            'Southern Europe': {'owner': None, 'troops': 0},
            'Ukraine': {'owner': None, 'troops': 0},
            'Ural': {'owner': None, 'troops': 0},
            'Venezuela': {'owner': None, 'troops': 0},
            'Western Australia': {'owner': None, 'troops': 0},
            'Western Europe': {'owner': None, 'troops': 0},
            'Western United States': {'owner': None, 'troops': 0},
            'Yakutsk': {'owner': None, 'troops': 0},
        }
        self.adjacency_map = {
            'Alaska': ['Alberta', 'Northwest Territory', 'Kamchatka'],
            'Alberta': ['Alaska', 'Northwest Territory', 'Ontario', 'Western United States'],
            'Argentina': ['Brazil', 'Peru'],
            'Brazil': ['Argentina', 'Peru', 'Venezuela', 'North Africa'],
            'Central America': ['Eastern United States', 'Western United States', 'Venezuela'],
            'China': ['Siam', 'India', 'Afghanistan', 'Ural', 'Siberia', 'Mongolia'],
            'Congo': ['North Africa', 'East Africa', 'South Africa'],
            'East Africa': ['Egypt', 'Congo', 'South Africa', 'Madagascar', 'Middle East', 'North Africa'],
            'Eastern Australia': ['New Guinea', 'Western Australia'],
            'Eastern United States': ['Western United States', 'Ontario', 'Quebec'],
            'Egypt': ['North Africa', 'East Africa', 'Middle East', 'Southern Europe'],
            'Great Britain': ['Iceland', 'Western Europe', 'Scandinavia', 'Northern Europe'],
            'Greenland': ['Northwest Territory', 'Ontario', 'Quebec', 'Iceland'],
            'Iceland': ['Greenland', 'Great Britain', 'Scandinavia'],
            'India': ['Middle East', 'Afghanistan', 'China', 'Siam'],
            'Indonesia': ['Siam', 'New Guinea', 'Western Australia'],
            'Irkutsk': ['Siberia', 'Yakutsk', 'Kamchatka', 'Mongolia'],
            'Japan': ['Kamchatka', 'Mongolia'],
            'Kamchatka': ['Alaska', 'Yakutsk', 'Irkutsk', 'Japan', 'Mongolia'],
            'Madagascar': ['East Africa', 'South Africa'],
            'Middle East': ['Southern Europe', 'Ukraine', 'Afghanistan', 'India', 'East Africa', 'Egypt'],
            'Mongolia': ['Irkutsk', 'Kamchatka', 'Japan', 'China', 'Siberia'],
            'New Guinea': ['Indonesia', 'Western Australia', 'Eastern Australia'],
            'North Africa': ['Brazil', 'Western Europe', 'Southern Europe', 'Egypt', 'East Africa', 'Congo'],
            'Northern Europe': ['Western Europe', 'Great Britain', 'Scandinavia', 'Ukraine', 'Southern Europe'],
            'Northwest Territory': ['Alaska', 'Alberta', 'Greenland', 'Ontario'],
            'Ontario': ['Alberta', 'Western United States', 'Eastern United States', 'Quebec', 'Northwest Territory', 'Greenland'],
            'Peru': ['Brazil', 'Argentina', 'Venezuela'],
            'Quebec': ['Ontario', 'Eastern United States', 'Greenland'],
            'Scandinavia': ['Iceland', 'Great Britain', 'Northern Europe', 'Ukraine'],
            'Siam': ['China', 'India', 'Indonesia'],
            'Siberia': ['Ural', 'Yakutsk', 'Irkutsk', 'Mongolia', 'China'],
            'South Africa': ['East Africa', 'Congo', 'Madagascar'],
            'Southern Europe': ['Western Europe', 'Northern Europe', 'Ukraine', 'Middle East', 'Egypt', 'North Africa'],
            'Ukraine': ['Scandinavia', 'Northern Europe', 'Southern Europe', 'Middle East', 'Afghanistan', 'Ural'],
            'Ural': ['Ukraine', 'Afghanistan', 'China', 'Siberia'],
            'Venezuela': ['Central America', 'Peru', 'Brazil'],
            'Western Australia': ['Indonesia', 'New Guinea', 'Eastern Australia'],
            'Western Europe': ['Great Britain', 'Northern Europe', 'Southern Europe', 'North Africa'],
            'Western United States': ['Alberta', 'Ontario', 'Eastern United States', 'Central America']
        }
        self.player_cards = {player: [] for player in self.players}
        self.continents = {
            'North America': ['Alaska', 'Alberta', 'Central America', 'Eastern United States', 'Greenland', 'Northwest Territory', 'Ontario', 'Quebec', 'Western United States'],
            'South America': ['Argentina', 'Brazil', 'Peru', 'Venezuela'],
            'Europe': ['Great Britain', 'Iceland', 'Northern Europe', 'Scandinavia', 'Southern Europe', 'Ukraine', 'Western Europe'],
            'Africa': ['Congo', 'East Africa', 'Egypt', 'Madagascar', 'North Africa', 'South Africa'],
            'Asia': ['Afghanistan', 'China', 'India', 'Irkutsk', 'Japan', 'Kamchatka', 'Middle East', 'Mongolia', 'Siam', 'Siberia', 'Ural', 'Yakutsk'],
            'Australia': ['Eastern Australia', 'Indonesia', 'New Guinea', 'Western Australia']
        }
        self.continent_values = {
            'North America': 5,
            'South America': 2,
            'Europe': 5,
            'Africa': 3,
            'Asia': 7,
            'Australia': 2
        }
        self.connections = {
            'Alaska': ['Alberta', 'Northwest Territory', 'Kamchatka'],
            'Alberta': ['Alaska', 'Northwest Territory', 'Ontario', 'Western United States'],
            'Central America': ['Eastern United States', 'Western United States', 'Venezuela'],
            'Eastern United States': ['Central America', 'Western United States', 'Quebec', 'Ontario'],
            'Greenland': ['Northwest Territory', 'Quebec', 'Iceland'],
            'Northwest Territory': ['Alaska', 'Alberta', 'Ontario', 'Greenland'],
            'Ontario': ['Northwest Territory', 'Alberta', 'Western United States', 'Eastern United States', 'Quebec'],
            'Quebec': ['Ontario', 'Eastern United States', 'Greenland'],
            'Western United States': ['Alberta', 'Ontario', 'Eastern United States', 'Central America'],
            'Argentina': ['Brazil', 'Peru'],
            'Brazil': ['Argentina', 'Peru', 'Venezuela', 'North Africa'],
            'Peru': ['Argentina', 'Brazil', 'Venezuela'],
            'Venezuela': ['Central America', 'Brazil', 'Peru'],
            'Great Britain': ['Iceland', 'Northern Europe', 'Scandinavia', 'Western Europe'],
            'Iceland': ['Greenland', 'Great Britain', 'Scandinavia'],
            'Northern Europe': ['Great Britain', 'Scandinavia', 'Southern Europe', 'Ukraine', 'Western Europe'],
            'Scandinavia': ['Iceland', 'Great Britain', 'Northern Europe', 'Ukraine'],
            'Southern Europe': ['Western Europe', 'Northern Europe', 'Ukraine', 'Middle East', 'Egypt', 'North Africa'],
            'Ukraine': ['Scandinavia', 'Northern Europe', 'Southern Europe', 'Middle East', 'Afghanistan', 'Ural'],
            'Western Europe': ['Great Britain', 'Northern Europe', 'Southern Europe', 'North Africa'],
            'Congo': ['North Africa', 'East Africa', 'South Africa'],
            'East Africa': ['Egypt', 'North Africa', 'Congo', 'South Africa', 'Madagascar', 'Middle East'],
            'Egypt': ['Southern Europe', 'Middle East', 'East Africa', 'North Africa'],
            'Madagascar': ['East Africa', 'South Africa'],
            'North Africa': ['Brazil', 'Western Europe', 'Southern Europe', 'Egypt', 'East Africa', 'Congo'],
            'South Africa': ['Congo', 'East Africa', 'Madagascar'],
            'Afghanistan': ['Ural', 'China', 'India', 'Middle East', 'Ukraine'],
            'China': ['Ural', 'Siberia', 'Mongolia', 'Siam', 'India', 'Afghanistan'],
            'India': ['Middle East', 'Afghanistan', 'China', 'Siam'],
            'Irkutsk': ['Siberia', 'Yakutsk', 'Kamchatka', 'Mongolia'],
            'Japan': ['Mongolia', 'Kamchatka'],
            'Kamchatka': ['Yakutsk', 'Irkutsk', 'Mongolia', 'Japan', 'Alaska'],
            'Middle East': ['Ukraine', 'Afghanistan', 'India', 'East Africa', 'Egypt', 'Southern Europe'],
            'Mongolia': ['Siberia', 'Irkutsk', 'Kamchatka', 'Japan', 'China'],
            'Siam': ['India', 'China', 'Indonesia'],
            'Siberia': ['Ural', 'Yakutsk', 'Irkutsk', 'Mongolia', 'China'],
            'Ural': ['Ukraine', 'Afghanistan', 'China', 'Siberia'],
            'Yakutsk': ['Siberia', 'Irkutsk', 'Kamchatka'],
            'Eastern Australia': ['Western Australia', 'New Guinea'],
            'Indonesia': ['Siam', 'New Guinea', 'Western Australia'],
            'New Guinea': ['Indonesia', 'Western Australia', 'Eastern Australia'],
            'Western Australia': ['Indonesia', 'New Guinea', 'Eastern Australia']
        }
        self.player_territories = player_territories
        self.cards = self.generate_cards()

    def generate_cards(self):
        types = ['Infantry', 'Cavalry', 'Artillery']
        cards = [{'territory': territory, 'type': types[i % len(types)]} for i, territory in enumerate(self.territories.keys())]
        random.shuffle(cards)
        return cards               

    def trade_cards_for_troops(self, player):
        if len(self.player_cards[player]) >= 3:
            types = [card['type'] for card in self.player_cards[player][:3]]
            territories = [card['territory'] for card in self.player_cards[player][:3]]
            if len(set(types)) == 1 or len(set(types)) == 3:  # Check if the first three cards are either all the same type or all different types
                trade_choice = input(f"Player {player}, do you want to trade in cards for troops? (yes/no): ")
                if trade_choice.lower() == 'yes':
                    self.player_cards[player] = self.player_cards[player][3:]
                    self.trade_in_count += 1
                    bonus_troops = max(4, self.trade_in_count * 2)  # The number of troops received depends on the number of sets traded in so far in the game
                    if all(territory in self.players[player] for territory in territories):  # Check if the player owns all of the territories on the cards
                        bonus_troops += 2  # Add 2 bonus troops
                    return bonus_troops
                elif trade_choice.lower() == 'no':
                    return 0  # Player chooses not to trade in cards, return 0 bonus troops
                else:
                    print("Invalid choice. Defaulting to not trading cards.")
        return 0

    def generate_game_map(self):    
        game_map = {}
        for territory in self.claim_territories:
            game_map[territory] = [adjacent_territory for adjacent_territory in game_map.get(territory, [])]
        self.adjacency_map = game_map  # Update adjacency_map
    
    def choose_territory_assignment_method(self):
        print("How would you like territories to be assigned?")
        print("1. Official Rules: Players claim territories in a round-robin fashion.")
        print("2. Shuffled Cards: Territories are distributed based on shuffled cards.")
        while True:
            choice = input("Enter your choice (1 or 2): ")
            if choice in ['1', '2']:
                return int(choice)
            else:
                print("Invalid choice. Please enter 1 or 2.")
    
    def assign_territories(self, method):
        if method == 2:
            self.random_distribution()
        else:
            self.claim_territories()

    def distribute_territories(self):
        method = int(input("How would you like territories to be assigned?\n1. Official Rules: Players claim territories in a round-robin fashion.\n2. Shuffled Cards: Territories are distributed based on shuffled cards.\nEnter your choice (1 or 2): "))
        self.assign_territories(method)
        
    def random_distribution(self):
        deck = list(self.territories.keys())
        random.shuffle(deck)
        num_players = len(self.players)
        territories_per_player = len(deck) // num_players
        for _ in range(territories_per_player):
            for player in self.players:
                territory = deck.pop(0)
                self.player_territories[player].append(territory)
                self.territories[territory]['owner'] = player

    def claim_territories(self):
        deck = list(self.territories.keys())
        random.shuffle(deck)
        while deck:
            for player in self.players:
                if deck:
                    territory = deck.pop(0)
                    self.player_territories[player].append(territory)
                    self.territories[territory]['owner'] = player

    def place_initial_armies(self):
        initial_armies = {2: 40, 3: 35, 4: 30, 5: 25, 6: 20}
        num_players = len(self.players)
        total_armies = initial_armies[num_players]
        for player in self.players:
            territories_owned = self.player_territories[player]  # Corrected to access player territories
            print(f"Player {player}, you have {total_armies} troops to place.")
            while total_armies > 0:
                print(f"Remaining troops: {total_armies}")
                territory = input("Enter the name of the territory where you want to place your troops (or type 'done' to end the setup phase): ")
                if territory.lower() == 'done':
                    break
                if territory not in territories_owned:
                    print("Invalid territory. You can only place troops on territories you own.")
                    continue
                try:
                    troops_to_place = input(f"Enter the number of troops you want to place on {territory} (0 to {total_armies}): ")
                    if troops_to_place.lower() == 'done':
                        break
                    troops_to_place = int(troops_to_place)
                    if troops_to_place < 0 or troops_to_place > total_armies:
                        print("Invalid number of troops. Please enter a number between 0 and the remaining troops.")
                        continue
                    if troops_to_place > 0:
                        self.territories[territory]['troops'] += troops_to_place
                        total_armies -= troops_to_place
                    else:
                        print("Skipping troop placement for this territory.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
 
    def start_game(self):
        self.distribute_territories()
        print("Distributing territories...")
        time.sleep(1)
        print("Placing initial armies...")
        time.sleep(1)
        self.place_initial_armies()
        print("Starting game...")
        while True:
            # Rotate the players list to simulate a clockwise turn order
            self.players = self.players[1:] + self.players[:1]
            for player in self.players:
                for player in list(self.players.keys()):
                    if player in self.players:  # Check if the player has not been eliminated
                        print(f"Player {player}'s turn")
                        # Trade in cards at the start of the turn if player has 5 or more cards
                        while len(self.player_cards[player]) >= 5:
                            self.trade_cards_for_troops(player)
                        self.reinforce_territories(player)
                        self.reinforce_territories(player)
                        conquered = self.attack_phase(player)
                        # Trade in cards after attack phase if player has 5 or more cards
                        while len(self.player_cards[player]) >= 5:
                            self.trade_cards_for_troops(player)
                        if conquered:
                            print(f"Player {conquered} has won the game!")
                            return
                        self.fortify_phase(player)
                        # Trade in cards after fortify phase if player has 5 or more cards
                        while len(self.player_cards[player]) >= 5:
                            self.trade_cards_for_troops(player)
                        # If the player has conquered a territory and there are cards left, give them a card
                        if self.cards and conquered:
                            self.player_cards[player].append(self.cards.pop())

    def ai_turn(self, player):
        print(f"AI Player {player}'s turn")
        time.sleep(1)
        print(f"AI Player {player} is trading cards for troops...")
        time.sleep(1)
        extra_troops = self.trade_cards_for_troops(player)
        print(f"AI Player {player} is receiving continent bonus troops...")
        time.sleep(1)
        extra_troops += self.continent_bonus(player)
        print(f"AI Player {player} is receiving territory bonus troops...")
        time.sleep(1)
        territories_owned = self.players[player]
        extra_troops += max(len(territories_owned) // 3, 3)
        print(f"AI Player {player} is deploying troops...")
        time.sleep(1)
        # Trade in cards at the start of the turn if AI player has 5 or more cards
        while len(self.player_cards[player]) >= 5:
            self.trade_cards_for_troops(player)
        # Reinforce territories adjacent to enemy territories, prioritizing those with a numerical disadvantage
        territories_to_reinforce = sorted([t for t in territories_owned if self.get_neighboring_enemy_territories(t)], key=lambda t: self.territories[t]['troops'])
        for _ in range(extra_troops):
            territory = territories_to_reinforce.pop(0)
            self.territories[territory]['troops'] += 1
        print(f"AI Player {player} has placed {extra_troops} troops on their territories.")
        print(f"AI Player {player} is attacking...")
        time.sleep(1)
        # Attack from territories where we have a numerical advantage, prioritizing those where the enemy has a numerical disadvantage
        for territory in sorted(territories_owned, key=lambda t: self.territories[t]['troops'], reverse=True):
            enemy_territories = self.get_neighboring_enemy_territories(territory)
            if enemy_territories:
                target_territory = min(enemy_territories, key=lambda t: self.territories[t]['troops'])
                self.attack(territory, target_territory)
        # Trade in cards after attack phase if AI player has 5 or more cards
        while len(self.player_cards[player]) >= 5:
            self.trade_cards_for_troops(player)
        print(f"AI Player {player} is fortifying...")
        time.sleep(1)
        # Move troops from territories not adjacent to enemy territories to territories adjacent to enemy territories, prioritizing those with a numerical disadvantage
        territories_to_fortify_from = [t for t in territories_owned if not self.get_neighboring_enemy_territories(t)]
        territories_to_fortify_to = sorted([t for t in territories_owned if self.get_neighboring_enemy_territories(t)], key=lambda t: self.territories[t]['troops'])
        if territories_to_fortify_from and territories_to_fortify_to:
            source = random.choice(territories_to_fortify_from)
            target = territories_to_fortify_to.pop(0)
            troops_to_move = self.territories[source]['troops'] - 1
            self.territories[source]['troops'] -= troops_to_move
            self.territories[target]['troops'] += troops_to_move
        # Trade in cards after fortify phase if AI player has 5 or more cards
        while len(self.player_cards[player]) >= 5:
            self.trade_cards_for_troops(player)

    def reinforce_territories(self, player):
        territories_owned = [territory for territory in self.territories if self.territories[territory]['owner'] == player]
        extra_troops = max(len(territories_owned) // 3, 3)
        extra_troops += self.trade_cards_for_troops(player)
        # Add continent bonus
        for continent, territories in self.continents.items():
            if all(self.territories[territory]['owner'] == player for territory in territories):
                extra_troops += self.continent_values[continent]
        while extra_troops > 0:
            print(f"You have {extra_troops} troops left to place.")
            territory = input("Enter the name of the territory where you want to place your troops (or type 'skip' to skip): ")
            if territory.lower() == 'skip':
                break  # Player chooses to skip troop placement
            if territory not in territories_owned:
                print("Invalid territory. You can only place troops on territories you own.")
                continue
            try:
                troops_to_place = int(input("Enter the number of troops you want to place on this territory: "))
                if troops_to_place > extra_troops:
                    print("You don't have that many troops left to place.")
                    continue
                if troops_to_place > 0:
                    self.territories[territory]['troops'] += troops_to_place
                    extra_troops -= troops_to_place
                else:
                    print("Skipping troop placement for this territory.")
            except ValueError:
                print("Invalid input. Please enter a number.")
            
    def attack(self, attacking_territory, defending_territory):
        if self.territories[attacking_territory]['troops'] > 1:
            attacking_troops = min(3, self.territories[attacking_territory]['troops'] - 1)
            defending_troops = min(2, self.territories[defending_territory]['troops'])
            attacker_dice = sorted([random.randint(1, 6) for _ in range(attacking_troops)], reverse=True)
            while True:
                try:
                    num_defender_dice = int(input(f"Defender, how many dice do you want to roll? (1 or 2): "))
                    if num_defender_dice in [1, 2]:
                        break
                    print("Invalid number of dice. Please enter 1 or 2.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
            defender_dice = sorted([random.randint(1, 6) for _ in range(num_defender_dice)], reverse=True)
            for a, d in zip(attacker_dice, defender_dice):
                if a > d:
                    self.territories[defending_territory]['troops'] -= 1
                else:
                    self.territories[attacking_territory]['troops'] -= 1
            if self.territories[defending_territory]['troops'] == 0:
                self.territories[defending_territory]['owner'] = self.territories[attacking_territory]['owner']
                while True:
                    troops_to_move = input(f"How many troops do you want to move to {defending_territory}? (0 to {attacking_troops}): ")
                    try:
                        troops_to_move = int(troops_to_move)
                        if 0 <= troops_to_move <= attacking_troops:
                            break
                        print(f"Invalid number of troops. Please enter a number between 0 and {attacking_troops}.")
                    except ValueError:
                        print("Invalid input. Please enter a number.")
                if troops_to_move > 0:
                    self.territories[attacking_territory]['troops'] -= troops_to_move
                    self.territories[defending_territory]['troops'] += troops_to_move
                self.check_elimination(self.territories[defending_territory]['owner'])
                return True
        return False

    def check_elimination(self, player):
        if not any(territory['owner'] == player for territory in self.territories.values()):
            print(f"Player {player} has been eliminated!")
            # Transfer cards of the eliminated player to the player who eliminated them
            for p, cards in self.player_cards.items():
                if player in cards:
                    self.player_cards[p].remove(player)
                    self.player_cards[self.territories[player]['owner']].append(player)
            del self.players[player] # Remove the player from the game   

    def attack_phase(self, player):
        territories_owned = self.players[player]
        has_attacked = False
        while True:
            valid_attack_from = [territory for territory in territories_owned if self.territories[territory]['troops'] > 1 and self.get_neighboring_enemy_territories(territory)]
            if not valid_attack_from:
                # If there are no valid territories to attack from, ask the player if they want to continue attacking
                continue_attack = input("Do you want to continue attacking? (yes/no): ")
                if continue_attack.lower() != 'yes':
                    return has_attacked if not isinstance(has_attacked, str) else False  # Return False if no attack is made during the turn
                else:
                    break  # If the player wants to continue attacking, break out of the loop and allow them to choose a territory to attack from
            for territory in valid_attack_from:
                enemy_territories = self.get_neighboring_enemy_territories(territory)
                while enemy_territories:
                    # Ask the player if they want to continue attacking
                    continue_attack = input("Do you want to continue attacking? (yes/no): ")
                    if continue_attack.lower() != 'yes':
                        return has_attacked if not isinstance(has_attacked, str) else False  # Return False if no attack is made during the turn
                    target_territory = max(enemy_territories, key=lambda t: self.territories[territory]['troops'] - self.territories[t]['troops'])
                    while self.territories[territory]['troops'] > 1 and self.territories[target_territory]['owner'] != player:
                        if target_territory in self.connections[territory]:  # Check if the target territory is adjacent to the attacking territory
                            num_dice_to_roll = int(input(f"How many dice do you want to roll when attacking {target_territory}? (1, 2, or 3): "))
                            if num_dice_to_roll in [1, 2, 3]:
                                if self.attack(territory, target_territory, num_dice_to_roll):
                                    has_attacked = True
                                    winner = self.check_win_condition()
                                    if winner:
                                        return winner
                                else:
                                    print("Invalid number of dice. Please enter 1, 2, or 3.")
                                    continue
                            else:
                                print("Invalid number of dice. Please enter 1, 2, or 3.")
                                continue
                    enemy_territories = [t for t in enemy_territories if self.territories[t]['owner'] != player and t in self.connections[territory]]  # Only consider territories that are connected to the current territory and owned by other players
        return has_attacked if not isinstance(has_attacked, str) else False

    def fortify(self, source, target):
        max_troops_to_move = self.territories[source]['troops'] - 1
        if max_troops_to_move > 0:
            while True:
                try:
                    troops_to_move = int(input(f"How many troops do you want to move from {source} to {target}? (Must be between 1 and {max_troops_to_move}): "))
                    if 1 <= troops_to_move <= max_troops_to_move:
                        break
                    print("Invalid number of troops. Please enter a valid number.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
            self.territories[source]['troops'] -= troops_to_move
            self.territories[target]['troops'] += troops_to_move
            
    def is_connected(self, source, target, player):
        visited = set()

        def dfs(territory):
            if territory == target:
                return True
            if self.territories[territory]['owner'] != player or territory in visited:
                return False
            visited.add(territory)
            return any(dfs(neighbour) for neighbour in self.connections[territory] if self.territories[neighbour]['owner'] == player)
        return dfs(source)

    def fortify_phase(self, player):
        fortify_choice = input("Do you want to fortify? Enter 'yes' or 'no': ")
        if fortify_choice.lower() == 'no':
            return  # End the fortify phase if the player chooses not to fortify at all
        territories_owned = self.players[player]
        fortified_pairs = set()  # Keep track of fortified pairs
        for territory in territories_owned:
            friendly_territories = self.get_neighboring_friendly_territories(territory)
            if friendly_territories:
                for target_territory in friendly_territories:
                    # Check if the pair has not been fortified yet and the territories are connected
                    if (territory, target_territory) not in fortified_pairs and self.is_connected(territory, target_territory, player):
                        fortify_choice = input(f"Do you want to fortify {territory} to {target_territory}? Enter 'yes' or 'no': ")
                        if fortify_choice.lower() == 'yes':
                            max_troops_to_move = self.territories[territory]['troops'] - 1
                            while True:
                                try:
                                    troops_to_move = int(input(f"How many troops do you want to move from {territory} to {target_territory}? (Must be between 1 and {max_troops_to_move}): "))
                                    if 1 <= troops_to_move <= max_troops_to_move:
                                        break
                                    print("Invalid number of troops. Please enter a valid number.")
                                except ValueError:
                                    print("Invalid input. Please enter a number.")
                            self.territories[territory]['troops'] -= troops_to_move
                            self.territories[target_territory]['troops'] += troops_to_move
                            fortified_pairs.add((territory, target_territory))  # Add the pair to the fortified pairs
                        elif fortify_choice.lower() == 'no':
                            continue  # Skip this pair and move to the next one
                        else:
                            print("Invalid choice. Please enter 'yes' or 'no'.")
                            continue  # Ask again for a valid choice
                    else:
                        print(f"The territories {territory} and {target_territory} are not eligible for fortification.")

    def get_neighboring_enemy_territories(self, territory):
        return [t for t in self.connections[territory] if self.territories[t]['owner'] != self.territories[territory]['owner']]

    def get_neighboring_friendly_territories(self, territory):
        return [t for t in self.connections[territory] if self.territories[t]['owner'] == self.territories[territory]['owner']]

    def check_win_condition(self):
        for player, territories in self.players.items():
            if len(territories) == len(self.territories):
                return player  # This player has won the game
        return False  # No player has won yet

players = ['AI Red', 'AI Blue', 'AI Green', 'AI Yellow', 'AI Black']
player_territories = {player: [] for player in players}

risk_game = RiskGame(player_territories)
risk_game.start_game()