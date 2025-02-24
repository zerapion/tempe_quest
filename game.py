from scenes import SceneManager, DialogueManager, SceneId, DialogueId
from char_types import CharacterType

from dataclasses import dataclass
from enum import Enum, auto

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.prompt import Prompt
from rich.theme import Theme
from rich.layout import Layout
from rich.live import Live
from rich.align import Align
"""
from prompt_toolkit import Application, PromptSession
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application import get_app
"""


# dataclass 'decorator' automatically generates methods like __init__ and __repr__
@dataclass
class Stats:
    passion: int
    intelligence: int
    charisma: int
    strength: int
    life: int
    patrick_points: int # this should be a secret stat, maybe seperete function for player to see stats without patrick point meter

    # check if current stat exists and is not above max of 10
    #   true: increment stat by 1
    #   false: fail
    # this should be simplified and more explicit, checks arent required i think. try, catch
    def level_up(self, stat_name: str) -> bool:
        if hasattr(self, stat_name) and getattr(self, stat_name) < 10:
            setattr(self, stat_name, getattr(self, stat_name) + 1)
            return True
        return False

# character class, combine stats and charactertype
class Character:
    def __init__(self, name: CharacterType, stats: Stats):
        self.name = name
        self.stats = stats

class Player:
    # dictionary 
    # set stats for each type
    def __init__(self):
        self.characters = {
            CharacterType.EVAN: Character(
                CharacterType.EVAN,
                Stats(passion=4, intelligence=3, charisma=4, strength=1, life=3, patrick_points=0)
            ),
            CharacterType.SEANP: Character(
                CharacterType.SEANP,
                Stats(passion=4, intelligence=4, charisma=2, strength=2, life=4, patrick_points=0)
            ),
            CharacterType.SEANH: Character(
                CharacterType.SEANH,
                Stats(passion=2, intelligence=0, charisma=1, strength=5, life=5, patrick_points=0)
            ),
            CharacterType.RYAN: Character(
                CharacterType.RYAN,
                Stats(passion=2, intelligence=2, charisma=2, strength=3, life=5, patrick_points=0)
            )
        }
        self.current_character = None

    # takes name, sanitize, set character if valid input
    def select_character(self, name: str) -> bool:
        try:
            character_type = CharacterType[name.upper()]
            self.current_character = self.characters[character_type]
            return True
        except KeyError:
            return False

    # return stats as dictionary (__dict__)
    #   print(player.get_stats())  # {'passion': 4, 'intelligence': 3, 'charisma': 4, 'strength': 1, 'life': 3}
    def get_stats(self) -> dict:
        if self.current_character:
            return self.current_character.stats.__dict__
        return {}
    
class WeaponType(Enum):
    PEPPERMINT_WAND = auto()


@dataclass
class Weapon:
    type: WeaponType
    name: str
    damage: int
    type: int


class Game:
    def __init__(self):
        custom_theme = Theme({
            "info": "cyan",
            "warning": "green",
            "error": "bold red",
            "title": "bold magenta",
            "prompt": "bold green",
            "heading": "bold blue"
        })


        self.console = Console(theme=custom_theme)
        self.player = Player()
        self.game_running = False

        self.layout = Layout()
        self.setup_layout()

    def setup_layout(self):
        # split into left and right
        self.layout.split_row(
            Layout(name="left_panel", ratio=1),
            Layout(name="right_panel", ratio=2)
        )

        self.layout["right_panel"].split_column(
            Layout(name="game_area", ratio=2),
            Layout(name="input_area", ratio=1)
        )

    def create_stats_panel(self):
        if not self.player.current_character:
            return Panel("No character select", title="Stats")
        
        stats = self.player.get_stats()
        stats_table = Table(show_header=False, box=None)
        stats_table.add_column("Stat", style="cyan")
        stats_table.add_column("Value", justify="right")
        
        for stat, value in stats.items():
            if stat != "patrick_points":  # Hide secret stat
                stats_table.add_row(stat.capitalize(), "★" * value)
                
        return Panel(stats_table, title="Character Stats")
    
    def update_display(self, game_text="", input_text=""):
        # Update left panel
        self.layout["left_panel"].update(self.create_stats_panel())
        
        # Update game area
        self.layout["game_area"].update(Panel(
            game_text,
            title="Tempe Quest",
            border_style="blue"
        ))
        
        # Update input area
        self.layout["input_area"].update(Panel(
            input_text,
            title="Actions",
            border_style="green"
        ))


    def display_title_screen(self):
        title = """
        ▄▄▄█████▓▓█████  ███▄ ▄███▓ ██▓███  ▓█████      █████   █    ██ ▓█████   ██████ ▄▄▄█████▓
        ▓  ██▒ ▓▒▓█   ▀ ▓██▒▀█▀ ██▒▓██░  ██▒▓█   ▀    ▒██▓  ██▒ ██  ▓██▒▓█   ▀ ▒██    ▒ ▓  ██▒ ▓▒
        ▒ ▓██░ ▒░▒███   ▓██    ▓██░▓██░ ██▓▒▒███      ▒██▒  ██░▓██  ▒██░▒███   ░ ▓██▄   ▒ ▓██░ ▒░
        ░ ▓██▓ ░ ▒▓█  ▄ ▒██    ▒██ ▒██▄█▓▒ ▒▒▓█  ▄    ░██  █▀ ░▓▓█  ░██░▒▓█  ▄   ▒   ██▒░ ▓██▓ ░ 
          ▒██▒ ░ ░▒████▒▒██▒   ░██▒▒██▒ ░  ░░▒████▒   ░▒███▒█▄ ▒▒█████▓ ░▒████▒▒██████▒▒  ▒██▒ ░ 
          ▒ ░░   ░░ ▒░ ░░ ▒░   ░  ░▒▓▒░ ░  ░░░ ▒░ ░   ░░ ▒▒░ ▒ ░▒▓▒ ▒ ▒ ░░ ▒░ ░▒ ▒▓▒ ▒ ░  ▒ ░░   
            ░     ░ ░  ░░  ░      ░░▒ ░      ░ ░  ░    ░ ▒░  ░ ░░▒░ ░ ░  ░ ░  ░░ ░▒  ░ ░    ░    
          ░         ░   ░      ░   ░░          ░         ░   ░  ░░░ ░ ░    ░   ░  ░  ░    ░      
                    ░  ░       ░                ░  ░      ░       ░        ░  ░      ░           
        """
        self.console.print(Panel(title, style="title"))
        self.console.print("\nWelcome to Tempe Quest!", style="heading")
        self.console.print("A text adventure through the depths of ASU reality", style="info")

        self.console.print("\nPress Enter to start...", style="prompt")
        input()

    def create_character_options(self) -> str:
        options =""
        for char_type in CharacterType:
            options += f"[green]-> {char_type.name.capitalize()}[/green]\n"
        return options

    def character_selection(self) -> bool:
        characters = list(CharacterType)
        
        # Create character selection table
        table = Table(show_header=True)
        table.add_column("Character", style="cyan")
        table.add_column("Passion", justify="center")
        table.add_column("Intelligence", justify="center")
        table.add_column("Charisma", justify="center")
        table.add_column("Strength", justify="center")
        table.add_column("Life", justify="center")

        for char_type in CharacterType:
            char = self.player.characters[char_type]
            stats = char.stats
            table.add_row(
                char_type.name.capitalize(),
                "★" * stats.passion,
                "★" * stats.intelligence,
                "★" * stats.charisma,
                "★" * stats.strength,
                "★" * stats.life
            )

        selected_preview = None

        with Live(self.layout, refresh_per_second=4, screen=True):
            self.update_display(
                game_text=f"\nChoose your character:\n\n{table}",
                input_text="Use number keys (1-4) to select:\n1. Evan\n2. SeanP\n3. SeanH\n4. Ryan\nPress Enter twice to confirm selection"
            )
            
            while True:
                choice = Prompt.ask("\nEnter your choice")
                
                if choice in ['1', '2', '3', '4']:
                    character_map = {
                        '1': 'EVAN',
                        '2': 'SEANP',
                        '3': 'SEANH',
                        '4': 'RYAN'
                    }
                    # Preview the character by temporarily selecting it
                    selected_preview = character_map[choice]
                    self.player.select_character(selected_preview)
                    self.update_display(
                        game_text=f"Selected {selected_preview.capitalize()}\nPress Enter to confirm or choose another number",
                        input_text="Use number keys (1-4) to select:\n1. Evan\n2. SeanP\n3. SeanH\n4. Ryan\n\nPress Enter to confirm selection"
                    )
                    
                elif choice == "" and selected_preview:
                    return True
                else:
                    self.console.print("Invalid choice. Please enter a number between 1 and 4.", style="error")
    
    
    def update_display(self, game_text="", input_text=""):
        # Update left panel
        self.layout["left_panel"].update(self.create_stats_panel())
        
        # Update game area
        self.layout["game_area"].update(Panel(
            game_text,
            title="Tempe Quest",
            border_style="blue"
        ))
        
        # Update input area
        self.layout["input_area"].update(Panel(
            input_text,
            title="Actions",
            border_style="green"
        ))

    def start(self):
        self.display_title_screen()
        if self.character_selection():
            self.game_running = True
            self.main_game_loop()
        else:
            with Live(self.layout, refresh_per_second=4, screen=True):
                self.update_display(game_text="Character selection failed!", input_text="Please restart the game")


    def main_game_loop(self):
        self.scene_manager = SceneManager()
        self.dialogue_manager = DialogueManager()
        
        with Live(self.layout, refresh_per_second=4, screen=True):
            while self.game_running:
                current_scene = self.scene_manager.get_current_scene()
                
                # Handle initial dialogue if scene has one
                if current_scene.initial_dialogue:
                    dialogue_state = self.dialogue_manager.start_dialogue(current_scene.initial_dialogue)
                    while dialogue_state:
                        # Display dialogue text
                        dialogue_text = dialogue_state.get_text(self.player.current_character.name)
                        choices_text = "\n".join(
                            f"{i+1}. {choice.text}" 
                            for i, choice in enumerate(dialogue_state.choices)
                        )
                        
                        self.update_display(
                            game_text=f"{dialogue_state.speaker}: {dialogue_text}",
                            input_text=choices_text
                        )
                        
                        # Get player choice
                        choice = Prompt.ask("\nSelect an option", choices=[
                            str(i+1) for i in range(len(dialogue_state.choices))
                        ])
                        
                        # Process choice
                        dialogue_state, next_scene = self.dialogue_manager.make_choice(
                            int(choice) - 1,
                            self.player.current_character.name
                        )
                        
                        # Handle scene transition if needed
                        if next_scene:
                            self.scene_manager.transition_to_scene(next_scene)
                            break
                
                # Display regular scene options when not in dialogue
                available_actions = current_scene.get_available_actions(
                    self.player.current_character.name,
                    self.player.get_stats()
                )
                
                actions_text = "\n".join(
                    f"{i+1}. {action.description}" 
                    for i, action in enumerate(available_actions)
                )
                
                self.update_display(
                    game_text=current_scene.description,
                    input_text=actions_text
                )
                
                # Get player choice
                choice = Prompt.ask("\nSelect an option", choices=[
                    str(i+1) for i in range(len(available_actions))
                ])
                
                # Process scene transition
                selected_action = available_actions[int(choice) - 1]
                self.scene_manager.transition_to_scene(selected_action.next_scene)

def main():
    game = Game()
    game.start()

if __name__ == "__main__":
    main()
