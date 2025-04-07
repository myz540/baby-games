from __future__ import annotations
import pygame
import sys
from typing import Dict, List, Optional
from enum import Enum
from pathlib import Path
from dataclasses import dataclass
from typing import Callable


class FighterState(Enum):
    IDLE = "idle"
    WALKING = "walking"
    TYPING = "typing"
    HURT = "hurt"
    ATTACK = "attack"  # New state for attack animation
    DEAD = "dead"
    JUMP = "jump"

class QTEventType(Enum):
    MOVE = "move"
    ATTACK = "attack"
    JUMP = "jump"
    DODGE = "dodge"
    BLOCK = "block"

class MonsterState(Enum):
    IDLE = "idle"
    HURT = "hurt"

@dataclass
class QTEvent:
    position: int  # x position where event triggers
    key: str  # key to press
    event_type: QTEventType  # type of event
    time_limit: int  # milliseconds to respond
    success_message: str  # message to display on success
    fail_message: str  # message to display on failure
    damage_on_fail: int = 0  # damage taken if failed
    trigger_distance: int = 100
    sprite: Optional['QTESprite'] = None
    
    def execute_success(self, fighter: Fighter):
        """Execute the successful action"""
        if self.event_type == QTEventType.MOVE:
            fighter.moving = True
        elif self.event_type == QTEventType.ATTACK:
            fighter.attack()
            if self.sprite:
                self.sprite.set_state(MonsterState.HURT)
        elif self.event_type == QTEventType.JUMP:
            fighter.jump()
        # Add more event types as needed

    def execute_failure(self, fighter: Fighter):
        """Execute the failure consequence"""
        fighter.set_state(FighterState.HURT)
        # Later we can add health system here
        print(self.fail_message)

class SpriteSheet:
    def __init__(self, frame_width: int, frame_height: int, sprite_paths: List[str] = None):
        # Expects a list of paths to individual frame images
        # Example: ["static/type_fighter/Male/attack_r_0.png", 
        #          "static/type_fighter/Male/attack_r_1.png",
        #          "static/type_fighter/Male/attack_r_2.png"]
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.frames: List[pygame.Surface] = []
        
        if sprite_paths:
            # Load actual sprite frames
            for path in sprite_paths:
                try:
                    image = pygame.image.load(str(path)).convert_alpha()  # Convert Path to string
                    # Scale image if needed
                    if image.get_width() != frame_width or image.get_height() != frame_height:
                        image = pygame.transform.scale(image, (frame_width, frame_height))
                    self.frames.append(image)
                except pygame.error as e:
                    print(f"Could not load sprite: {path}, error: {e}")
                    # Create fallback colored rectangle
                    surface = pygame.Surface((frame_width, frame_height))
                    surface.fill((255, 0, 0))
                    self.frames.append(surface)
        else:
            # Fallback to colored rectangles as before
            colors = [(255, 0, 0), (200, 0, 0), (150, 0, 0), (100, 0, 0)]
            for color in colors:
                surface = pygame.Surface((frame_width, frame_height))
                surface.fill(color)
                self.frames.append(surface)
    
    def get_frame(self, index: int) -> pygame.Surface:
        if not self.frames:
            # Create an emergency fallback frame if no frames are loaded
            surface = pygame.Surface((self.frame_width, self.frame_height))
            surface.fill((255, 0, 0))
            return surface
        # Ensure we don't get an index error by using modulo
        return self.frames[index % len(self.frames)]

class Animation:
    def __init__(self, sprite_sheet: SpriteSheet, frame_duration: int):
        self.sprite_sheet = sprite_sheet
        self.frame_duration = frame_duration  # milliseconds per frame
        self.current_frame = 0
        self.last_update = 0
        
    def update(self, current_time: int) -> pygame.Surface:
        if current_time - self.last_update > self.frame_duration:
            self.current_frame += 1
            self.last_update = current_time
        
        return self.sprite_sheet.get_frame(self.current_frame)

class Fighter:
    def __init__(self, x: int, y: int, gender: str = "male"):
        self.gender = gender.lower()
        self.animations: Dict[FighterState, Animation] = {}
        self.setup_animations()
        
        self.current_state = FighterState.IDLE
        self.rect = pygame.Rect(x, y, 80, 120)
        self.moving = True
        self.speed = 3
        self.facing_right = True
        
        # Add jump physics
        self.initial_y = y  # Store initial y position
        self.y_velocity = 0
        self.jump_speed = -18  # Increased for higher jump
        self.gravity = 0.7  # Reduced for slower fall
        self.is_jumping = False
    
    def setup_animations(self):
        base_path = Path("static/type_fighter")
        
        # Define animation data with actual sprite paths
        animation_data = {
            FighterState.IDLE: (
                80, 120, 200,  # width, height, duration
                [base_path / self.gender / f"idle_{i}.png" for i in range(4)]  # if you have 4 idle frames
            ),
            FighterState.WALKING: (
                80, 120, 150,
                [base_path / self.gender / f"run_{i}.png" for i in range(4)]  # if you have 4 walking frames
            ),
            FighterState.DEAD: (
                80, 120, 120,
                [base_path / self.gender / f"death_{i}.png" for i in range(4)]  # if you have 2 dead frames
            ),
            FighterState.TYPING: (
                80, 120, 100,
                [base_path / self.gender / f"idle_{i}.png" for i in range(2)]  # if you have 2 typing frames
            ),
            FighterState.ATTACK: (
                80, 120, 100,
                [base_path / self.gender / f"attack_r_{i}.png" for i in range(3)]  # your 3 attack frames
            ),
            FighterState.JUMP: (
                80, 120, 100,
                [base_path / self.gender / f"jump_{i}.png" for i in range(2)]  # your 2 jump frames
            ),
        }
        
        for state, (width, height, duration, paths) in animation_data.items():
            sprite_sheet = SpriteSheet(width, height, paths if paths else None)
            self.animations[state] = Animation(sprite_sheet, duration)
    
    def set_state(self, new_state: FighterState):
        if self.current_state != new_state:
            self.current_state = new_state
            # Reset animation when state changes
            self.animations[self.current_state].current_frame = 0
    
    def draw(self, screen: pygame.Surface):
        current_time = pygame.time.get_ticks()
        frame = self.animations[self.current_state].update(current_time)
        
        # Flip the frame if facing left
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)
        
        screen.blit(frame, self.rect)
    
    def jump(self):
        if not self.is_jumping:  # Only jump if not already jumping
            self.is_jumping = True
            self.y_velocity = self.jump_speed
            self.set_state(FighterState.JUMP)

    def update_physics(self):
        if self.is_jumping:
            # Apply gravity
            self.y_velocity += self.gravity
            self.rect.y += self.y_velocity

            # Check if landed
            if self.rect.y >= self.initial_y:
                self.rect.y = self.initial_y
                self.y_velocity = 0
                self.is_jumping = False
                if self.moving:
                    self.set_state(FighterState.WALKING)
                else:
                    self.set_state(FighterState.IDLE)

    def move(self):
        if self.moving:
            self.rect.x += self.speed
            if not self.is_jumping:
                self.set_state(FighterState.WALKING)
        else:
            if not self.is_jumping:
                self.set_state(FighterState.IDLE)
        
        self.update_physics()  # Update jump physics each frame
    
    def attack(self):
        self.set_state(FighterState.ATTACK)
        # You might want to add a callback or timer to return to IDLE
        # after the attack animation completes

class QTESprite:
    def __init__(self, x: int, y: int, width: int, height: int, monster_type: str = "blue", scale: float = 1.0):
        # Apply scale to width and height
        self.scale = scale
        self.original_width = width
        self.original_height = height
        self.scaled_width = int(width * scale)
        self.scaled_height = int(height * scale)
        
        # Center the sprite at the original position
        x_offset = (width - self.scaled_width) // 2
        y_offset = (height - self.scaled_height) // 2
        
        self.rect = pygame.Rect(x + x_offset, y + y_offset, self.scaled_width, self.scaled_height)
        self.state = MonsterState.IDLE
        self.monster_type = monster_type
        self.animations: Dict[MonsterState, Animation] = {}
        self.setup_animations()
        self.last_update = 0
        
    def setup_animations(self):
        base_path = Path("static/type_fighter/monsters") / self.monster_type
        
        # Define animation data
        animation_data = {
            MonsterState.IDLE: (
                self.original_width, self.original_height, 200,  # width, height, duration
                [base_path / f"idle_{i}.png" for i in range(2)]  # Assuming 2 idle frames
            ),
            MonsterState.HURT: (
                self.original_width, self.original_height, 150,
                [base_path / f"hurt_{i}.png" for i in range(1)]  # Assuming 1 hit frames
            ),
        }
        
        for state, (width, height, duration, paths) in animation_data.items():
            sprite_sheet = SpriteSheet(width, height, paths)
            self.animations[state] = Animation(sprite_sheet, duration)
    
    def set_state(self, new_state: MonsterState):
        if self.state != new_state:
            self.state = new_state
            # Reset animation when state changes
            self.animations[self.state].current_frame = 0
    
    def draw(self, screen: pygame.Surface):
        current_time = pygame.time.get_ticks()
        frame = self.animations[self.state].update(current_time)
        
        # Scale the frame if needed
        if self.scale != 1.0:
            frame = pygame.transform.scale(frame, (self.scaled_width, self.scaled_height))
        
        screen.blit(frame, self.rect)

class TypeFighter:
    def __init__(self):
        pygame.init()
        self.screen_size = (800, 600)
        self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption("Type Fighter")
        
        # Center the fighter horizontally
        self.fighter = Fighter(self.screen_size[0] // 3, 400)  # Lowered by 300 pixels

        self.font = pygame.font.Font(None, 36)
        
        # World offset tracks total movement
        self.world_offset = 0
        
        # Background (we'll need two copies to create infinite scroll)
        try:
            self.background = pygame.image.load("static/type_fighter/background.jpg").convert()
            self.background = pygame.transform.scale(self.background, (self.screen_size[0], self.screen_size[1]))
        except pygame.error:
            self.background = pygame.Surface(self.screen_size)
            self.background.fill((20, 20, 50))  # Dark blue-gray fallback
        
        self.background_width = self.background.get_width()
        self.background_x = 0
        
        self.clock = pygame.time.Clock()
        
        # Define the sequence of quick time events
        self.qt_events = [
            QTEvent(
                position=700,
                key='a',
                event_type=QTEventType.ATTACK,
                time_limit=2000,
                success_message="First strike!",
                fail_message="Missed the opening!",
                damage_on_fail=10,
                trigger_distance=70,
                sprite=QTESprite(700, 400, 80, 120, "blue", scale=0.5)
            ),
            QTEvent(
                position=1400,
                key='j',
                event_type=QTEventType.JUMP,
                time_limit=1500,
                success_message="Aerial maneuver!",
                fail_message="Couldn't get airborne!",
                damage_on_fail=15,
                trigger_distance=70,
                sprite=QTESprite(1400, 400, 80, 120, "blue", scale=0.5)
            ),
            QTEvent(
                position=2000,
                key='k',
                event_type=QTEventType.ATTACK,
                time_limit=2000,
                success_message="Finishing blow!",
                fail_message="Failed to finish!",
                damage_on_fail=20,
                trigger_distance=70,
                sprite=QTESprite(2000, 400, 80, 120, "blue", scale=0.5)
            ),
        ]
        self.current_event_index = 0
        
        # Prompt state
        self.waiting_for_input = False
        self.current_event: Optional[QTEvent] = None
        self.prompt_start_time = 0
        
        # Animation state
        self.animation_timer = 0
        self.animation_complete = True

    def update_world(self):
        if self.animation_complete and self.fighter.moving:
            # Instead of moving fighter, move the world
            self.world_offset += self.fighter.speed
            
            # Update background position
            self.background_x -= self.fighter.speed
            # Reset background position when it moves off screen
            if self.background_x <= -self.background_width:
                self.background_x = 0

    def draw_background(self):
        # Draw two copies of the background side by side
        self.screen.blit(self.background, (self.background_x, 0))
        self.screen.blit(self.background, (self.background_x + self.background_width, 0))

    def show_prompt(self, event: QTEvent):
        self.waiting_for_input = True
        self.current_event = event
        self.prompt_start_time = pygame.time.get_ticks()
        self.fighter.moving = False
        self.fighter.set_state(FighterState.TYPING)
        
    def check_prompt_timeout(self) -> bool:
        if not self.waiting_for_input or not self.current_event:
            return False
        
        elapsed = pygame.time.get_ticks() - self.prompt_start_time
        return elapsed > self.current_event.time_limit
    
    def draw_prompt(self):
        if self.waiting_for_input and self.current_event:
            # Draw the event type
            event_text = self.font.render(
                f"{self.current_event.event_type.value.upper()}: Press {self.current_event.key}", 
                True, 
                (255, 255, 255)
            )
            text_rect = event_text.get_rect(center=(self.screen_size[0] // 2, 100))
            self.screen.blit(event_text, text_rect)
            
            # Draw time remaining
            elapsed = pygame.time.get_ticks() - self.prompt_start_time
            remaining = max(0, (self.current_event.time_limit - elapsed) / 1000)
            timer = self.font.render(f"Time: {remaining:.1f}", True, (255, 255, 255))
            timer_rect = timer.get_rect(center=(self.screen_size[0] // 2, 150))
            self.screen.blit(timer, timer_rect)
    
    def handle_animation_completion(self):
        """Handle the completion of an animation and return to appropriate state"""
        current_time = pygame.time.get_ticks()
        if not self.animation_complete and current_time >= self.animation_timer:
            self.animation_complete = True
            self.fighter.moving = True  # Ensure movement is enabled after animation
            # Don't force state change if jumping
            if not self.fighter.is_jumping:
                if self.fighter.moving:
                    self.fighter.set_state(FighterState.WALKING)
                else:
                    self.fighter.set_state(FighterState.IDLE)

    def start_animation(self, duration: int):
        """Start an animation with a specific duration"""
        self.animation_complete = False
        self.animation_timer = pygame.time.get_ticks() + duration

    def handle_event_success(self):
        """Handle successful QTE completion"""
        if not self.current_event:
            return

        print(self.current_event.success_message)
        
        # Execute the event action
        self.current_event.execute_success(self.fighter)
        
        # Set animation timer based on event type
        if self.current_event.event_type == QTEventType.ATTACK:
            # Duration for attack animation (3 frames)
            self.start_animation(self.fighter.animations[FighterState.ATTACK].frame_duration * 3)
        elif self.current_event.event_type == QTEventType.JUMP:
            # For jump, we'll let the physics system handle the duration
            self.start_animation(self.fighter.animations[FighterState.JUMP].frame_duration * 4)
        
        self.waiting_for_input = False
        self.current_event = None
        self.fighter.moving = True  # Ensure fighter resumes movement after animation

    def main(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if self.waiting_for_input and self.current_event:
                        if event.unicode == self.current_event.key:
                            self.handle_event_success()
                        else:
                            self.current_event.execute_failure(self.fighter)
                            self.start_animation(self.fighter.animations[FighterState.HURT].frame_duration * 2)
            
            # Handle animation completion
            self.handle_animation_completion()
            
            # Only check for new events if not waiting and animation is complete
            if (not self.waiting_for_input and 
                self.animation_complete and
                self.current_event_index < len(self.qt_events) and 
                self.world_offset >= self.qt_events[self.current_event_index].position - self.fighter.rect.x - self.qt_events[self.current_event_index].trigger_distance):
                self.show_prompt(self.qt_events[self.current_event_index])
                self.current_event_index += 1
            
            # Check for timeout
            if self.check_prompt_timeout() and self.current_event:
                self.current_event.execute_failure(self.fighter)
                self.start_animation(self.fighter.animations[FighterState.HURT].frame_duration * 2)
                self.waiting_for_input = False
                self.current_event = None
            
            # Update world position instead of moving fighter
            self.update_world()
            
            # Update fighter physics regardless of movement state
            self.fighter.update_physics()
            
            # Draw
            self.draw_background()
            
            # Draw all remaining QTE sprites (adjusted for world offset)
            for event in self.qt_events[self.current_event_index:]:
                if event.sprite:
                    # Adjust sprite position based on world offset
                    sprite_screen_x = event.position - self.world_offset
                    event.sprite.rect.x = sprite_screen_x
                    # Only draw if on screen
                    if -event.sprite.rect.width <= sprite_screen_x <= self.screen_size[0]:
                        event.sprite.draw(self.screen)
            
            # Draw the current QTE sprite if there is one
            if self.waiting_for_input and self.current_event and self.current_event.sprite:
                sprite_screen_x = self.current_event.position - self.world_offset
                self.current_event.sprite.rect.x = sprite_screen_x
                if -self.current_event.sprite.rect.width <= sprite_screen_x <= self.screen_size[0]:
                    self.current_event.sprite.draw(self.screen)
            
            self.fighter.draw(self.screen)
            self.draw_prompt()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()

def main():
    game = TypeFighter()
    game.main()

if __name__ == "__main__":
    main()
