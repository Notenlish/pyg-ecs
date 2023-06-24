import random
import typing
import pygame
import pygame_ecs
from pygame_ecs.components.base_component import BaseComponent


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
    def __init__(self, screen) -> None:
        super().__init__(required_component_types=[Position, BallRenderer])
        self.screen = screen

    def update(self, entity_components):
        for i, comp in enumerate(entity_components):
            if type(comp) == Position:
                pos: Position = comp  # type: ignore
            if type(comp) == BallRenderer:
                ball_renderer: BallRenderer = comp  # type: ignore
        pygame.draw.circle(self.screen, ball_renderer.color, (pos.x, pos.y), ball_renderer.radius)  # type: ignore


class BallPhysics(pygame_ecs.BaseSystem):
    def __init__(self, screen) -> None:
        super().__init__(required_component_types=[Position, Velocity])
        self.dt = 0
        self.screen = screen

    def update(self, entity_components):
        for i, comp in enumerate(entity_components):
            if type(comp) == Position:
                pos: Position = comp  # type: ignore
            if type(comp) == Velocity:
                vel: Velocity = comp  # type: ignore
        pos.x += vel.vec.x * self.dt  # type: ignore
        pos.y += vel.vec.y * self.dt  # type: ignore
        if pos.x > self.screen.get_width() or pos.x < 0:
            vel.vec.x *= -1
        if pos.y > self.screen.get_height() or pos.y < 0:
            vel.vec.y *= -1

class App:
    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()
        self.dt = 0

    def setup(self):
        self.entities = []
        self.entity_manager = pygame_ecs.EntityManager()
        self.component_manager = pygame_ecs.ComponentManager()
        self.system_manager = pygame_ecs.SystemManager()
        self.ball_draw_system = BallDrawSystem(self.screen)
        self.ball_physics = BallPhysics(self.screen)

    def add_entities(self):
        for _ in range(100):
            center = (
                random.randint(0, self.screen.get_width()),
                random.randint(0, self.screen.get_height()),
            )
            radius = random.randint(4, 15)
            color = [random.randint(0, 255) for _ in range(3)]
            vel = pygame.math.Vector2(
                (random.random() - 0.5) * 400 / 1000,
                (random.random() - 0.5) * 400 / 1000,
            )
            entity = self.entity_manager.add_entity(self.component_manager)
            self.component_manager.add_component(entity, Position(center[0], center[1]))
            self.component_manager.add_component(entity, BallRenderer(radius, color))
            self.component_manager.add_component(entity, Velocity(vel))
            self.entities.append(entity)

    def draw(self):
        self.screen.fill("black")
        self.system_manager.update_entities(
            self.entities, self.component_manager, self.ball_draw_system
        )

    def run(self):
        self.setup()
        self.add_entities()
        while True:
            self.get_input()
            self.update()
            self.draw()
            self.dt = self.clock.tick(60)
            pygame.display.update()

    def update(self):
        self.ball_physics.dt = self.dt
        self.system_manager.update_entities(
            self.entities, self.component_manager, self.ball_physics
        )

    def get_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise SystemExit


if __name__ == "__main__":
    app = App()
    app.run()
