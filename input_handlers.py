from __future__ import annotations
import tcod


from tcod.event import EventDispatch, KeyDown, K_ESCAPE

from engine import Engine

class EventHandler(EventDispatch[None]):
    def __init__(self) -> None:
        super().__init__()
        self.engine = Engine.instance()

    def handle_events(self, event: tcod.event.Event) -> EventHandler:
        """Handle events for input handlers with an engine."""
        self.dispatch(event)
        return self

    def ev_mousemotion(self, event: tcod.event.MouseMotion) -> None:
        if self.engine.game_map.in_bounds(event.tile.x, event.tile.y):
            self.engine.mouse_location = event.tile.x, event.tile.y

    def ev_keydown(self, event: KeyDown) -> None:
        key = event.sym
        if key == K_ESCAPE:
            raise SystemExit()
        return super().ev_keydown(event)

    def on_render(self, console: tcod.Console) -> None:
        self.engine.render(console)
