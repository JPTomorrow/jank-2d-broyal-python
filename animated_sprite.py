import pygame

_anim_store: set = {}

class SpriteAnimation:
    
    def __init__(self, name: str, spritesheet_path: str, frame_count, frame_width, frame_height, frame_duration = .1):
        self.name = name
        self.sprite = pygame.image.load(spritesheet_path).convert_alpha() # sprite sheet
        self.frame_count = frame_count # number of uniform frames in spritesheet
        self.frame_elapsed = 0.0
        self.frame_duration = frame_duration # duration of a frame in seconds
        self.frame_width = frame_width
        self.frame_height = frame_height
        def empty():
            print("empty animation func")
        self.finished_func = empty
        
        _add_to_anim_set(self)

    @staticmethod
    def play(name, finished_func):
        anim : SpriteAnimation
        for a in _anim_store:
            if a.name == name:
                anim = a
        
        if anim is None:
            print("did not find animation")
            return
            
        # play the animation

def _add_to_anim_set(anim):
    _anim_store.add(anim)