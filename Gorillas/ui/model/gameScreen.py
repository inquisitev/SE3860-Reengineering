import winsound

import pygame
import pygame_gui
from ui.model.elements.sprites.windArrow import WindArrow
from ui.model.elements.sprites.banana import Banana
from ui.model.elements.sprites.collisions import Collisions
from ui.model.model import Model
from color import Color
from ui.model.elements.sprites.sun import Sun
from ui.model.elements.sprites.gorilla import Gorilla
from Backend.Controllers.GameController import GameController
from ui.model.elements.sprites.building import Building
from Backend.Adapters.CoordinateAdapter import CoordinateAdapter
from pygame_gui.core.interfaces import IContainerLikeInterface
import utils
from typing import Union


class PlayerInputPanel(pygame_gui.elements.ui_panel.UIPanel):
    PANEL_SIZE = (300, 200)

    def __init__(self, panel_pos: (int, int), player_id: str,
                 manager: pygame_gui.core.interfaces.manager_interface.IUIManagerInterface,
                 container: Union[IContainerLikeInterface, None] = None):
        self._rect = pygame.Rect(panel_pos, self.PANEL_SIZE)
        super(PlayerInputPanel, self).__init__(self._rect, 0, manager, container=container)

        self._PLAYER_LABEL_RECT = pygame.Rect(0, 5, 240, 20)

        self._ANGLE_LABEL_RECT = pygame.Rect(5, 40, 80, 20)
        self._ANGLE_BOX_RECT = pygame.Rect(85, 40, 210, 20)

        self._VELOCITY_LABEL_RECT = pygame.Rect(5, 80, 80, 20)
        self._VELOCITY_BOX_RECT = pygame.Rect(85, 80, 210, 20)

        self._LAUNCH_BUTTON_RECT = pygame.Rect(0, 115, 240, 60)

        self.player_label = pygame_gui.elements.UILabel(relative_rect=self._PLAYER_LABEL_RECT,
                                                        text="Player: " + player_id,
                                                        manager=manager,
                                                        container=self)
        self.player_label.set_relative_position(
            (self._rect.width / 2 - self.player_label.relative_rect.centerx, self.player_label.relative_rect.y))

        self.angle_label = pygame_gui.elements.UILabel(relative_rect=self._ANGLE_LABEL_RECT,
                                                       text="Angle:",
                                                       manager=manager,
                                                       container=self)

        self.angle_box = pygame_gui.elements.ui_text_entry_line.UITextEntryLine(relative_rect=self._ANGLE_BOX_RECT,
                                                                                manager=manager,
                                                                                container=self)
        self.angle_box.set_allowed_characters("numbers")

        self.velocity_label = pygame_gui.elements.UILabel(relative_rect=self._VELOCITY_LABEL_RECT,
                                                          text="Velocity:",
                                                          manager=manager,
                                                          container=self, )

        self.velocity_box = pygame_gui.elements.ui_text_entry_line.UITextEntryLine(
            relative_rect=self._VELOCITY_BOX_RECT,
            manager=manager,
            container=self)
        self.velocity_box.set_allowed_characters("numbers")

        self.launch_button = pygame_gui.elements.UIButton(relative_rect=self._LAUNCH_BUTTON_RECT,
                                                          text="Throw Banana",
                                                          container=self,
                                                          manager=manager)
        self.launch_button.set_relative_position(
            (self._rect.width / 2 - self.launch_button.relative_rect.centerx, self.launch_button.relative_rect.y))

    def update(self, time_delta: float):
        super().update(time_delta)
        if not self.is_enabled\
                or not utils.isint(self.angle_box.get_text()) \
                or not utils.isint(self.velocity_box.get_text()) \
                or float(self.angle_box.get_text()) <= 0 \
                or int(self.velocity_box.get_text()) <= 0:
            self.launch_button.disable()
        else:
            self.launch_button.enable()


class GameScreenPanel(pygame_gui.elements.ui_panel.UIPanel):

    def __init__(self, player_1_id, player_2_id, gravity, max_score,
                 parent_rect: pygame.Rect,
                 manager: pygame_gui.core.interfaces.manager_interface.IUIManagerInterface):
        self._rect = parent_rect.copy()
        super(GameScreenPanel, self).__init__(self._rect, 0, manager)
        self._playerids = [player_1_id, player_2_id]

        self._game_rect = pygame.Rect(0, 0, self._rect.width, self._rect.height - PlayerInputPanel.PANEL_SIZE[1])
        self.game_surface_element = pygame_gui.elements.UIImage(self._game_rect,
                                                                pygame.Surface(self._rect.size).convert(),
                                                                manager=manager,
                                                                container=self,
                                                                parent_element=self)

        self.max_score = max_score
        self.gameModel = GameScreenModel(self._game_rect.size, player_1_id, player_2_id, gravity, max_score)

        player_one_input_panel_pos = (0, self._rect.height - PlayerInputPanel.PANEL_SIZE[1])
        self.player_one_input_panel = PlayerInputPanel(player_one_input_panel_pos, player_1_id,
                                                       manager=manager, container=self)

        player_two_input_panel_pos = (self._rect.width - PlayerInputPanel.PANEL_SIZE[0],
                                      self._rect.height - PlayerInputPanel.PANEL_SIZE[1])
        self.player_two_input_panel = PlayerInputPanel(player_two_input_panel_pos, player_2_id,
                                                       manager=manager, container=self)

    def update(self, time_delta: float):
        super().update(time_delta)
        self.gameModel.update()
        self.gameModel.draw(self.game_surface_element.image)
        if self.gameModel.game_state.turn_active:
            self.player_one_input_panel.disable()
            self.player_two_input_panel.disable()
        elif self.gameModel.game_state.active_player().player_id == self._playerids[0]:
            self.player_one_input_panel.enable()
            self.player_two_input_panel.disable()
        else:
            self.player_two_input_panel.enable()
            self.player_one_input_panel.disable()

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Process the launch buttons
        :param event: The event to process.
        :return: Should return True if this element makes use of this event.
        """
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.player_one_input_panel.launch_button:
                    self.gameModel.game_controller.throw_projectile(float(self.player_one_input_panel.angle_box.get_text()),
                                                                    float(self.player_one_input_panel.velocity_box.get_text()))
                    winsound.PlaySound("sounds\\throw.wav", winsound.SND_ASYNC | winsound.SND_ALIAS)
                    return True
                elif event.ui_element == self.player_two_input_panel.launch_button:
                    self.gameModel.game_controller.throw_projectile(float(self.player_two_input_panel.angle_box.get_text()),
                                                                    float(self.player_two_input_panel.velocity_box.get_text()))
                    winsound.PlaySound("sounds\\throw.wav", winsound.SND_ASYNC | winsound.SND_ALIAS)
                    return True


class GameScreenModel(Model):
    """The main screen of the game"""

    BACKGROUND_COLOR = Color.BLUE
    GORILLA_IMAGE = pygame.image.load("Sprites/Doug/doug.png")
    GORILLA_LEFT = pygame.image.load("Sprites/Doug/dougLeft.png")
    GORILLA_RIGHT = pygame.image.load("Sprites/Doug/dougRight.png")

    def __init__(self, screen_size, player_1_id, player_2_id, gravity, max_score):
        super(GameScreenModel, self).__init__(self.BACKGROUND_COLOR)
        self.render.append(pygame.sprite.Group())  # Building Layer
        self.render.append(pygame.sprite.Group())  # Main Layer
        self.render.append(pygame.sprite.Group())  # UI Layer

        self.player_pos = {player_1_id: 0, player_2_id: 1}

        self.coordinate_adapter = CoordinateAdapter(screen_size)
        self.game_controller = GameController(player_1_id, player_2_id, screen_size, max_score, gravity=gravity)
        self.game_state = self.coordinate_adapter.adapt(self.game_controller.next_frame())

        # Create the background
        self.background = pygame.Surface(screen_size)
        self.background = self.background.convert()
        self.background.fill(self.BACKGROUND_COLOR)
        # Create the Sun object. Won't move.
        sun_width = screen_size[0] / 20
        sun_height = screen_size[1] / 30
        sun_x_pos = (screen_size[0] - sun_width) / 2
        sun_y_pos = (screen_size[1] - sun_height) / 10
        self.sun = Sun(sun_width, sun_height, sun_x_pos, sun_y_pos)
        self.render[1].add(self.sun)
        # Create the buildings
        self.buildings = []
        for building in self.game_state.building:
            building_pos = (building.x_pos, building.y_pos - building.height)
            building_pos = (building.x_pos, building.y_pos - 14)
            building_size = (building.width, building.height * 1.5)
            new_building = Building(building.color, building_pos, building_size)
            self.render[0].add(new_building)
            self.buildings.append(new_building)
        # Create player one's gorilla
        self.gorilla_one = self.create_gorilla(self.game_state.gorillas[0], self.game_state.building[0],
                                               self.GORILLA_IMAGE)
        self.render[1].add(self.gorilla_one)
        # Create player two's gorilla
        self.gorilla_two = self.create_gorilla(self.game_state.gorillas[1], self.game_state.building[0],
                                               self.GORILLA_IMAGE)
        self.render[1].add(self.gorilla_two)

        # Create the wind arrow
        self.wind_arrow = WindArrow(self.game_state.wind.direction, self.game_state.wind.velocity, screen_size)
        self.render[2].add(self.wind_arrow)
        # Create a list to store destruction in
        self.collision_list = []
        self.collision_num = 0
        # Create a projectile placeholder to use when updating the scene
        # May need to update in later revisions if there are multiple projectiles
        self.projectile = Banana((30, 20), (0, 0))
        self.projectile.transparent()
        self.render[1].add(self.projectile)
        # Blit the objects to the background
        self.background.blit(self.sun.image, self.sun.rect)
        for building in self.buildings:
            self.background.blit(building.image, building.rect)
        self.background.blit(self.gorilla_one.image, self.gorilla_one.rect)
        self.background.blit(self.gorilla_two.image, self.gorilla_two.rect)
        """Space to add other UI elements in later when Adam is ready"""
        self.background.blit(self.wind_arrow.image, self.wind_arrow.rect)
        self.background.blit(self.projectile.image, self.projectile.rect)
        pygame.display.update()

    def create_gorilla(self, gorilla, building, image):
        """Creates a UI Gorilla object from given data"""

        pos = (gorilla.x_pos, gorilla.y_pos)
        dimensions = (gorilla.width, gorilla.height)
        new_gorilla = Gorilla(dimensions, pos, image)
        return new_gorilla

    def update_frame(self, frame):
        """Updates the background to be a new frame of the game"""
        # Update the gorillas
        if frame.gorillas[0].arm_state == frame.gorillas[0].arm_state.ARM_DOWN:
            self.gorilla_one.image = self.GORILLA_IMAGE
        elif frame.gorillas[0].arm_state == frame.gorillas[0].arm_state.LEFT_ARM_UP:
            self.gorilla_one.image = self.GORILLA_LEFT
        elif frame.gorillas[0].arm_state == frame.gorillas[0].arm_state.RIGHT_ARM_UP:
            self.gorilla_one.image = self.GORILLA_RIGHT

        if frame.gorillas[1].arm_state == frame.gorillas[1].arm_state.ARM_DOWN:
            self.gorilla_two.image = self.GORILLA_IMAGE
        elif frame.gorillas[1].arm_state == frame.gorillas[1].arm_state.LEFT_ARM_UP:
            self.gorilla_two.image = self.GORILLA_LEFT
        elif frame.gorillas[1].arm_state == frame.gorillas[1].arm_state.RIGHT_ARM_UP:
            self.gorilla_two.image = self.GORILLA_RIGHT

        # Update the projectile
        if frame.turn_active:
            if len(frame.active_projectiles) > 0:
                projectile_pos = (frame.active_projectiles[0].current_x, frame.active_projectiles[0].current_y)
                self.projectile.rect = pygame.Rect(projectile_pos[0], projectile_pos[1], self.projectile.size[0],
                                                   self.projectile.size[1])
                self.projectile.visible()

        # Create collisions if a new collision has appeared
        if self.collision_num < len(frame.destruction):
            new_collision = Collisions(frame.destruction[self.collision_num])
            self.collision_list.append(new_collision)
            self.render[1].add(new_collision)
            self.background.blit(self.collision_list[self.collision_num].image,
                                 self.collision_list[self.collision_num].rect)
            self.collision_num = self.collision_num + 1
            self.projectile.transparent()

        # Update the wind
        new_width = frame.wind.velocity * self.wind_arrow.WIND_DEFAULT_WIDTH
        self.wind_arrow.image = pygame.transform.scale(self.wind_arrow.image, (new_width, self.wind_arrow.WIND_HEIGHT))
        if self.wind_arrow.direction != frame.wind.direction:
            self.wind_arrow.image = pygame.transform.flip(self.wind_arrow.image, True, False)
        self.wind_arrow.rect = pygame.Rect(self.wind_arrow.wind_pos[0], self.wind_arrow.wind_pos[1], new_width,
                                           self.wind_arrow.WIND_HEIGHT)

    def update(self):
        """Get the next frame from game state and update render"""
        pre_adapt_state = self.game_controller.next_frame()
        self.game_state = self.coordinate_adapter.adapt(pre_adapt_state)
        if self.game_state.turn_active:
            pygame.time.Clock().tick(45)
        else:
            pygame.time.Clock().tick(60)
        self.update_frame(self.game_state)
