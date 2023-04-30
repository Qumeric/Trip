#!/usr/bin/env python3
import time
import traceback

import tcod

from engine import Engine
from example.populate_island import populate_island
from game_map.island_generator import generate_island
from input_handlers import EventHandler

# TODO engine is the same always, need to pickle game_map instead, it stores stuff.
# def save_game(handler: input_handlers.BaseEventHandler, filename: str) -> None:
#     """If the current event handler has an active Engine then save it."""
#     if isinstance(handler, input_handlers.EventHandler):
#         handler.engine.save_as(filename)
#         print("Game saved.")


# def load_game(filename: str) -> Engine:
#     """Load an Engine instance from a file."""
#     with open(filename, "rb") as f:
#         engine = pickle.loads(lzma.decompress(f.read()))
#     assert isinstance(engine, Engine)
#     return engine


def new_game() -> Engine:
    """Return a brand new game session as an Engine instance."""

    # player = entity_factories.create_player()

    # engine.game_map = generate_dungeon(
    #     max_rooms=max_rooms,
    #     room_min_size=room_min_size,
    #     room_max_size=room_max_size,
    #     map_width=constants.map_width,
    #     map_height=constants.map_height,
    #     max_monsters_per_room=max_monsters_per_room,
    #     max_items_per_room=max_items_per_room,
    #     engine=engine,
    # )

    map_width = 160
    map_height = 100

    island = generate_island(map_width, map_height)
    engine = Engine.instance(game_map=island)
    populate_island(island)
    island.update_fov()
    # player.parent = engine.game_map
    # engine.game_map.entities.add(player)
    # player._update_fov()

    return engine


def main() -> None:
    engine: Engine = new_game()
    screen_width = engine.game_map.width
    screen_height = engine.game_map.height

    # OLD: tileset = tcod.tileset.load_tilesheet("dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD)
    tileset = tcod.tileset.load_truetype_font("whitrabt.ttf", 16, 16)

    # handler: input_handlers.BaseEventHandler = setup_game.MainMenu()

    ticks_per_minute = 60
    tick_rate = 60 / ticks_per_minute
    fps = 30
    event_timeout = 1 / fps

    with tcod.context.new(
        columns=screen_width,
        rows=screen_height,
        tileset=tileset,
        title="Trip",
        vsync=True,
    ) as context:
        last_tick_time = time.time()
        root_console = tcod.Console(screen_width, screen_height, order="F")
        handler = EventHandler()
        try:
            while True:
                current_time = time.time()

                if current_time - last_tick_time >= tick_rate:
                    engine.tick()
                    last_tick_time = current_time

                root_console.clear()
                # engine.render(console=root_console)
                handler.on_render(console=root_console)
                context.present(root_console)

                for event in tcod.event.wait(timeout=event_timeout):
                    try:
                        context.convert_event(event)
                        handler = handler.handle_events(event)
                    except Exception:  # Handle exceptions in game.
                        traceback.print_exc()  # Print error to stderr.
        # except exceptions.QuitWithoutSaving:
        #     raise
        except SystemExit:  # Save and quit.
            # save_game(handler, "savegame.sav")
            raise
        # except BaseException:  # Save on any other unexpected exception.
        #     save_game(handler, "savegame.sav")
        #     raise


if __name__ == "__main__":
    main()
