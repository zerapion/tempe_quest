from dataclasses import dataclass
from typing import List, Dict, Optional, Callable, Tuple
from enum import Enum, auto
from char_types import CharacterType

# scene ids ranging from 1 to n
class SceneId(Enum):
    BEDROOM = auto()
    MARGO = auto()
    MARGO_DR_MARIO = auto()
    HOMEDEPOT = auto()
    PALM_WALK = auto()  # needed for zoo exit

    """ sugar slums """
    SUGAR_SLUMS = auto()
    SUGAR_DADDYS = auto()
    MITCHELL_PARK = auto()
    BELOW_ETL = auto()

    """ zoo """
    ZOO = auto()
    GORILLA_ENCLOSURE = auto()

    """ ETEMP ACADEMY """
    ETEMP_ACADEMY = auto()

    """ ETEMP MARKETPLACE """
    ETEMP_MARKET = auto()


class DialogueId(Enum):
    """ DR MARIO """
    DR_MARIO_INIT = auto()
    DR_MARIO_QUEST_PROMPT = auto()
    DR_MARIO_YES = auto()
    DR_MARIO_NO = auto()

    """ HOME DEPOT """
    DESPOT_GREETING = auto()
    DESPOT_ATTACK = auto()
    DESPOT_HALF_HEALTH = auto()
    DESPOT_DEALTH = auto()

    ONLOOKER_1 = auto()
    ONLOOKER_2 = auto()

    """ SUGAR DADDY """
    """ DUDS """


@dataclass
class DialogueChoice:
    text: str                                        # what player sees in action box
    next_dialogue: Optional[DialogueId] = None       # next dialogue state if continuing conversation
    next_scene: Optional[SceneId] = None            # next scene if ending conversation
    stat_check: Optional[Dict[str, int]] = None     # required stats for this choice
    conditions: Optional[Dict[str, bool]] = None     # game state conditions
    next_scene_generator: Optional[Callable] = None  # dynamic scene transition based on character


@dataclass
class DialogueState:
    id: DialogueId                           # current dialogue state
    speaker: str                             # who is talking
    text: Optional[str] = None               # static dialogue text
    text_generator: Optional[Callable] = None # dynamic text based on character
    choices: List[DialogueChoice] = None      # available responses

    def get_text(self, character: Optional[CharacterType] = None) -> str:
        """Get appropriate text based on whether it's static or dynamic"""
        if self.text_generator and character:
            return self.text_generator(character)
        return self.text or ""


class DialogueManager:
    def __init__(self):
        self.current_dialogue = None
        self.dialogues = {
            DialogueId.DR_MARIO_INIT: DialogueState(
                id=DialogueId.DR_MARIO_INIT,
                speaker="Dr. Mario",
                text="Good morning, chile.",
                choices=[
                    DialogueChoice(
                        text="Good morning",
                        next_dialogue=DialogueId.DR_MARIO_QUEST_PROMPT,
                    )
                ]
            ),
            DialogueId.DR_MARIO_QUEST_PROMPT: DialogueState(
                id=DialogueId.DR_MARIO_QUEST_PROMPT,
                speaker="Dr. Mario",
                text="Do you feel prepared?",
                choices=[
                    DialogueChoice(
                        text="Yes",
                        next_dialogue=DialogueId.DR_MARIO_YES,
                    ),
                    DialogueChoice(
                        text="No",
                        next_dialogue=DialogueId.DR_MARIO_NO,
                    )
                ]
            ),
            DialogueId.DR_MARIO_YES: DialogueState(
                id=DialogueId.DR_MARIO_YES,
                speaker="Dr. Mario",
                text_generator=lambda character: {
                    CharacterType.EVAN: "*takes deep breath* Go forth my child, to the Sugar Slums",
                    CharacterType.SEANH: "*takes deep breath* Go forth my child, to the Zoo",
                    CharacterType.SEANP: "*takes deep breath* Go forth my child, to the Etemp Academy",
                    CharacterType.RYAN: "*takes deep breath* Go forth my child, to the Etemp Marketplace"
                }[character],
                choices=[
                    DialogueChoice(
                        text="Go forth",
                        next_scene_generator=lambda character: {
                            CharacterType.EVAN: SceneId.SUGAR_SLUMS,
                            CharacterType.SEANH: SceneId.ZOO,
                            CharacterType.SEANP: SceneId.ETEMP_ACADEMY,
                            CharacterType.RYAN: SceneId.ETEMP_MARKET
                        }[character]
                    )
                ]
            ),
            DialogueId.DR_MARIO_NO: DialogueState(
                id=DialogueId.DR_MARIO_NO,
                speaker="Dr. Mario",
                text="You should go to Home Depot",
                choices=[
                    DialogueChoice(
                        text="Go to Home Depot",
                        next_scene=SceneId.HOMEDEPOT
                    )
                ]
            )
        }
    
    def start_dialogue(self, dialogue_id: DialogueId) -> DialogueState:
        """Start or transition to a new dialogue state"""
        self.current_dialogue = self.dialogues[dialogue_id]
        return self.current_dialogue
    
    def make_choice(self, choice_index: int, character: CharacterType) -> Tuple[Optional[DialogueState], Optional[SceneId]]:
        """Process player's dialogue choice and determine next state
        Returns:
        - Tuple of (next_dialogue, next_scene)
        - If next_dialogue is None but next_scene isn't: end dialogue and transition to scene
        - If next_dialogue isn't None but next_scene is None: continue dialogue
        """
        if not self.current_dialogue:
            return None, None
            
        choice = self.current_dialogue.choices[choice_index]
        
        # Handle scene transitions (both static and dynamic)
        if choice.next_scene_generator:
            return None, choice.next_scene_generator(character)
        if choice.next_scene:
            return None, choice.next_scene
            
        # Handle dialogue progression
        if choice.next_dialogue:
            return self.start_dialogue(choice.next_dialogue), None
            
        return None, None


# what appears in action box
@dataclass
class Action:
    description: str                                      # what player sees
    next_scene: SceneId                                  # where this leads
    required_character: Optional[CharacterType] = None    # character restriction
    stat_requirements: Optional[Dict[str, int]] = None   # stat requirements
    
    # check if character matches action and if they pass skill check
    def is_available(self, character: CharacterType, stats: Dict[str, int]) -> bool:
        if self.required_character and character != self.required_character:
            return False
            
        if self.stat_requirements:
            return all(stats.get(stat, 0) >= value 
                      for stat, value in self.stat_requirements.items())
        return True


# what appears in tempe quest box
@dataclass
class Scene:
    id: SceneId
    description: str
    actions: List[Action]                            # available actions
    initial_dialogue: Optional[DialogueId] = None    # dialogue to start when entering scene

    # return list of available actions based off of character and stats
    def get_available_actions(self, character: CharacterType, stats: Dict[str, int]) -> List[Action]:
        return [action for action in self.actions 
                if action.is_available(character, stats)]


# scene controller
class SceneManager:
    def __init__(self):
        self.scenes: Dict[SceneId, Scene] = self._initialize_scenes()
        self.current_scene_id = SceneId.BEDROOM
    
    # map ids to scenes
    def _initialize_scenes(self) -> Dict[SceneId, Scene]:
        return {
            SceneId.BEDROOM: Scene(
                id=SceneId.BEDROOM,
                description="You wake up and scratch your ass",
                actions=[
                    Action("Scratch your ass", SceneId.BEDROOM),
                    Action("Leave room", SceneId.MARGO)
                ]
            ),
            SceneId.MARGO: Scene(
                id=SceneId.MARGO,
                description="Margo common area",
                actions=[
                    Action("Talk to Dr. Mario", SceneId.MARGO_DR_MARIO),
                    Action("Go to the Sugar Slums", SceneId.SUGAR_SLUMS, CharacterType.EVAN),
                ]
            ),
            SceneId.MARGO_DR_MARIO: Scene(
                id=SceneId.MARGO_DR_MARIO,
                description="You approach Dr. Mario. He stares intently into your eyes.",
                initial_dialogue=DialogueId.DR_MARIO_INIT,
                actions=[
                    Action("Leave", SceneId.MARGO)  # Changed from "Talk to Dr. Mario" to avoid loop
                ]
            ),
            SceneId.ZOO: Scene(
                id=SceneId.ZOO,
                description="""The Phoenix Zoo stretches before you. You can hear various animal 
                sounds in the distance.""",
                actions=[
                    Action(
                        "Enter gorilla enclosure", 
                        SceneId.GORILLA_ENCLOSURE,
                        required_character=CharacterType.SEANH,
                        stat_requirements={"strength": 3}
                    ),
                    Action("Leave zoo", SceneId.PALM_WALK)
                ]
            ),
            # Add more scenes here
        }
    
    def get_current_scene(self) -> Scene:
        """Get the current scene object"""
        return self.scenes[self.current_scene_id]
    
    def transition_to_scene(self, scene_id: SceneId) -> bool:
        """Attempt to transition to a new scene"""
        if scene_id in self.scenes:
            self.current_scene_id = scene_id
            return True
        return False
