import random
import sys

# --- Base Entity Class ---
class Entity:
    """Base class for all interactive objects (Player and Bugs)."""
    def __init__(self, name, health, attack):
        self.name = name
        self.max_health = health
        self.health = health
        self.attack = attack

    def is_alive(self):
        """Check if the entity is still alive."""
        return self.health > 0

    def take_damage(self, damage):
        """Reduces health and returns the damage taken."""
        self.health -= damage
        print(f"[{self.name}] takes {damage} damage! Health: {max(0, self.health)}/{self.max_health}")
        if self.health <= 0:
            print(f"--- [{self.name}] has been eliminated! ---")

# --- Player Class ---
class Player(Entity):
    """The main player entity (The Developer)."""
    def __init__(self, name="The Developer"):
        # Corrected __init__ call
        super().__init__(name, health=100, attack=15)
        self.inventory = []
        self.current_location = 0 # Index in the Game.MAP list
        self.features_collected = 0

    def add_feature(self, feature_name):
        """Adds a collected 'feature' (item) to the inventory."""
        self.inventory.append(feature_name)
        self.features_collected += 1
        self.max_health += 5 # Permanent buff for every feature collected
        self.health = min(self.max_health, self.health + 10) # Small heal
        print(f"\n[Feature Collected]: You implemented '{feature_name}'! (+5 Max HP, +10 HP)")
        print(f"Current Max HP: {self.max_health}")

    def show_status(self):
        """Displays the player's current stats and inventory."""
        print("-" * 30)
        print(f"| STATUS REPORT: {self.name}")
        print(f"| Health: {self.health}/{self.max_health}")
        print(f"| Attack Power: {self.attack}")
        print(f"| Features Collected: {self.features_collected}")
        print(f"| Inventory: {', '.join(self.inventory) if self.inventory else 'Empty'}")
        print("-" * 30)

# --- Bug (Enemy) Class ---
class Bug(Entity):
    """An enemy entity (The Bug)."""
    def __init__(self, level):
        name = random.choice(["Runtime Error", "Segmentation Fault", "Off-by-One Loop", "Null Pointer"])
        health = 20 + (level * 10)
        attack = 5 + (level * 5)
        # Corrected __init__ call
        super().__init__(name, health, attack)
        self.level = level
        print(f"\n[BUG ALERT]: A Level {self.level} {self.name} has appeared!")

# --- Game Logic Class ---
class Game:
    """Manages the main game loop, map, and core mechanics."""
    # Define the "System" map: Name, Exits (N, E, S, W), Initial Content (Bug/Feature)
    MAP = [
        {"name": "Main Repository", "exits": {'N': 1, 'E': 2}, "content": None},
        {"name": "Frontend Component", "exits": {'S': 0, 'E': 3}, "content": "Bug"},
        {"name": "Backend Service", "exits": {'W': 0, 'N': 3}, "content": "Feature: Authentication"},
        {"name": "Database Schema", "exits": {'S': 2, 'W': 1}, "content": "Bug"},
        {"name": "CI/CD Pipeline", "exits": {}, "content": "Feature: Automated Testing"},
    ]
    
    # Static list of features to pull from
    FEATURE_POOL = ["User Profiles", "API Caching", "Real-time Notifications", "Data Migration Script", "Linter Configuration"]

    def __init__(self):
        self.player = Player()
        self.is_running = True
        self.current_bug = None
        self.map_state = [d.copy() for d in self.MAP] # Deep copy of the map
        # Fill in the remaining features in the map
        feature_map_locations = [4] # CI/CD Pipeline already has one
        # Add a couple more features to the map state
        self.map_state[2]['content'] = f"Feature: {self.FEATURE_POOL.pop(0)}" # Authentication
        self.map_state[4]['content'] = f"Feature: {self.FEATURE_POOL.pop(0)}" # Automated Testing
        
        print("--- Code Debugger Adventure: The Software Engineering RPG ---")
        print("Goal: Collect features and squash all bugs to ship the final product!")
        print("Type 'help' for commands.\n")
        self._authenticate_user()

    def _authenticate_user(self):
        """Simulates initial setup and authentication."""
        auth_token = random.randint(1000, 9999)
        print(f"Initializing system... Auth Token: {auth_token}")
        self.player.show_status()
        self._look()

    def _look(self):
        """Prints the current location details."""
        location = self.map_state[self.player.current_location]
        print(f"\n[CURRENT LOCATION]: You are in the {location['name']}.")
        
        # Display exits
        exit_str = ", ".join(f"[{d}]" for d in location['exits'].keys())
        print(f"Available Exits: {exit_str if exit_str else 'None (Dead End)'}")
        
        # Display content
        content = location['content']
        if content:
            if "Bug" in content:
                # If there's a bug, initialize it for combat if not already active
                if not self.current_bug or not self.current_bug.is_alive() or self.player.current_location != self.map_state.index(location):
                    # Only create a new bug instance if one isn't already active in this room
                    if not self.current_bug or not self.current_bug.is_alive():
                         # Determine bug level based on location or progress
                        bug_level = 1 + (self.player.features_collected // 2) + self.player.current_location // 2
                        self.current_bug = Bug(bug_level)

                print(f"!!! WARNING: A Bug detected in this module! You must 'attack' it!")
                print(f"Bug Health: {self.current_bug.health}/{self.current_bug.max_health}")
            elif content.startswith("Feature:"):
                print(f"[*] Found a valuable {content}! Type 'collect' to implement it.")
            else:
                print(f"[DATA]: There is an unknown artifact here: {content}")
        else:
            print("[STATUS]: Module clean. No outstanding issues or features.")

    def _move(self, direction):
        """Handles player movement between locations."""
        direction = direction.upper()
        location = self.map_state[self.player.current_location]
        
        if self.current_bug and self.current_bug.is_alive() and self.map_state.index(location) == self.player.current_location:
            print("\n[BLOCKED]: You must 'attack' and squash the active bug before moving!")
            return

        if direction in location['exits']:
            new_index = location['exits'][direction]
            self.player.current_location = new_index
            self._look()
        else:
            print("\n[INVALID MOVE]: You can't go that way. Check the available exits.")

    def _start_combat(self):
        """Initializes or continues combat with a Bug."""
        location = self.map_state[self.player.current_location]
        content = location['content']

        if not content or "Bug" not in content:
            print("\n[DEBUGGING]: There is no bug to attack here. Proceed with caution.")
            return

        # Initialize the bug if it's the first attack or the bug was defeated and we are starting combat again
        if not self.current_bug or not self.current_bug.is_alive() or self.map_state.index(location) != self.player.current_location:
            # Determine bug level based on player progress and location
            bug_level = 1 + (self.player.features_collected // 2) + self.player.current_location // 2
            self.current_bug = Bug(bug_level)
            print("Combat initiated! Use the 'attack' command to fight.")

    def _attack(self):
        """Performs one round of combat."""
        if not self.current_bug or not self.current_bug.is_alive():
            self._start_combat()
            if not self.current_bug or not self.current_bug.is_alive():
                print("\n[SYSTEM]: No active combat target.")
                return

        bug = self.current_bug
        player = self.player

        # Player attacks first (Your Code Attack)
        player_damage = random.randint(player.attack - 5, player.attack + 5)
        print(f"\n> You debug and commit a change, dealing {player_damage} damage to the {bug.name}!")
        bug.take_damage(player_damage)

        if not bug.is_alive():
            print(f"\n[SUCCESS]: You have squashed the {bug.name}!")
            self.map_state[self.player.current_location]['content'] = None # Clear the bug from the map
            self.current_bug = None
            self.player.health = min(player.max_health, player.health + 5) # Small reward heal
            print("You receive a small health boost for eliminating the threat.")
            # After victory, show the location status
            self._look()
            return

        # Bug attacks back (The Bug Strikes)
        bug_damage = random.randint(bug.attack - 3, bug.attack + 3)
        print(f"> The {bug.name} retaliates and causes a crash, dealing {bug_damage} damage to you!")
        player.take_damage(bug_damage)

        if not player.is_alive():
            self.is_running = False
            print("\n[GAME OVER]: Your system crashed. The project failed. You couldn't squash the bug.")
            print(f"You managed to collect {self.player.features_collected} features before failing.")

    def _collect(self):
        """Handles collecting features/items."""
        location = self.map_state[self.player.current_location]
        content = location['content']
        
        if content and content.startswith("Feature:"):
            feature_name = content.split(": ")[1]
            self.player.add_feature(feature_name)
            location['content'] = None # Remove the feature from the map
            
            # Check for win condition
            # Total features available are the 5 from the MAP list originally
            total_features_to_win = 5
            
            if self.player.features_collected >= total_features_to_win:
                self.is_running = False
                print("\n" + "=" * 50)
                print("!!! PROJECT SHIPPED SUCCESSFULLY !!!")
                print("You have collected all critical features and squashed all known bugs.")
                print(f"FINAL STATS: Max HP: {self.player.max_health}, Features: {self.player.features_collected}")
                print("=" * 50)
            else:
                # After collecting, look around again
                self._look()
        else:
            print("\n[NOTE]: Nothing valuable to collect here.")


    def _show_help(self):
        """Displays available commands."""
        print("-" * 30)
        print("Available Commands:")
        print("  move [N/E/S/W]: Move in a direction.")
        print("  look: Check your current location and contents.")
        print("  attack: Engage a bug in combat.")
        print("  collect: Pick up a feature (item).")
        print("  status: Show player health, attack, and inventory.")
        print("  quit: Exit the game.")
        print("-" * 30)

    def run(self):
        """The main game loop."""
        while self.is_running:
            try:
                # Prompt the user for input
                command_input = input("\n> What do you do? ").strip().lower()
                
                if not command_input:
                    continue
                
                parts = command_input.split()
                command = parts[0]
                argument = parts[1] if len(parts) > 1 else ""

                if command == 'quit':
                    self.is_running = False
                    print("Exiting Code Debugger Adventure. Work in progress...")
                elif command == 'help':
                    self._show_help()
                elif command == 'look':
                    self._look()
                elif command == 'status':
                    self.player.show_status()
                elif command == 'move':
                    self._move(argument)
                elif command == 'attack':
                    self._attack()
                elif command == 'collect':
                    self._collect()
                else:
                    print(f"[ERROR]: Unknown command '{command}'. Type 'help' for a list of commands.")

            except Exception as e:
                # Catch general errors (like index out of bounds on split if command is complex)
                print(f"\n[SYSTEM ERROR]: An unexpected error occurred: {e}. Please try again.")
                
# --- Main Execution Block ---
if __name__ == "__main__":
    game = Game()
    game.run()
