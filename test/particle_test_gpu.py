import pygame
import random
import pygame_ecs
from pygame._sdl2 import Renderer, Texture, Window, get_drivers

pygame.init()

ENTITY_AMOUNT = 1_000 * 10
WIDTH = 800
HEIGHT = 600


class Position(pygame_ecs.BaseComponent):
    def __init__(self, x: int, y: int):
        super().__init__()
        self.x = x
        self.y = y


class BallRenderer(pygame_ecs.BaseComponent):
    def __init__(self, radius: int, color) -> None:
        super().__init__()
        self.radius = radius
        self.color = color


class Velocity(pygame_ecs.BaseComponent):
    def __init__(self, vec: pygame.math.Vector2) -> None:
        super().__init__()
        self.vec = vec


class BallDrawSystem(pygame_ecs.BaseSystem):
    def __init__(self, renderer, texture) -> None:
        super().__init__(required_component_types=[Position, BallRenderer])
        self.renderer = renderer
        self.texture = texture

    def update(self, entity_components):
        pos: Position = entity_components[Position]  # type: ignore
        ball_renderer: BallRenderer = entity_components[BallRenderer]  # type: ignore

        self.texture.color = ball_renderer.color  # type: ignore
        self.texture.draw(
            None, (pos.x, pos.y, ball_renderer.radius, ball_renderer.radius)
        )


class BallPhysics(pygame_ecs.BaseSystem):
    def __init__(self, screen) -> None:
        super().__init__(required_component_types=[Position, Velocity])
        self.dt = 0
        self.screen = screen

    def update(self, entity_components):
        pos: Position = entity_components[Position]  # type: ignore
        vel: Velocity = entity_components[Velocity]  # type: ignore
        pos.x += vel.vec.x * self.dt  # type: ignore
        pos.y += vel.vec.y * self.dt  # type: ignore
        if pos.x > WIDTH or pos.x < 0:
            vel.vec.x *= -1
        if pos.y > HEIGHT or pos.y < 0:
            vel.vec.y *= -1


screen = pygame.display.set_mode((WIDTH, HEIGHT))
window = Window.from_display_module()
renderer = Renderer(window, accelerated=1)

texture = Texture.from_surface(renderer, pygame.image.load("test/circle.png"))

entities = []
entity_manager = pygame_ecs.EntityManager()
component_manager = pygame_ecs.ComponentManager()
system_manager = pygame_ecs.SystemManager()
ball_physics = BallPhysics(screen)
ball_draw_system = BallDrawSystem(renderer=renderer, texture=texture)

component_manager.add_component_type(Position)
component_manager.add_component_type(Velocity)
component_manager.add_component_type(BallRenderer)


for _ in range(ENTITY_AMOUNT):
    center = (
        random.randint(0, WIDTH),
        random.randint(0, HEIGHT),
    )
    radius = random.randint(5, 15)
    color = [255, 255, 255]
    color.append(255)
    vel = pygame.math.Vector2(
        (random.random() - 0.5) * 400 / 1000,
        (random.random() - 0.5) * 400 / 1000,
    )
    entity = entity_manager.add_entity(component_manager)
    component_manager.add_component(entity, Position(center[0], center[1]))
    component_manager.add_component(entity, Velocity(vel))
    component_manager.add_component(entity, BallRenderer(radius, color))
    entities.append(entity)


clock = pygame.time.Clock()
dt = 0

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
    renderer.draw_color = (
        0,
        0,
        0,
        255,
    )  # type: ignore # renderer.draw_color is used for clearing the screen and drawing primitives
    renderer.clear()

    ball_physics.dt = dt
    system_manager.update_entities(entities, component_manager, ball_physics)
    system_manager.update_entities(entities, component_manager, ball_draw_system)
    renderer.present()

    dt = clock.tick(60)
    pygame.display.set_caption(f"FPS: {clock.get_fps()}")

pygame.quit()
