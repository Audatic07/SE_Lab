"""Capture actual Pygame surfaces from deterministic, explicitly staged scenarios."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame

ROOT = Path(__file__).resolve().parents[1]


def capture(source, phase):
    spec = importlib.util.spec_from_file_location("captured_game", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    pygame.init()
    screen = pygame.display.set_mode((module.WIDTH, module.HEIGHT))
    random.seed(36)
    records = []

    def scene():
        game = module.Game()
        # Keep the wave open while each focused scenario is exercised.
        game.to_spawn, game.spawn_timer = 1, 999
        return game

    def save(game, filename, description):
        game.draw(screen)
        pygame.display.flip()
        pygame.image.save(screen, str(ROOT / "screenshots" / filename))
        records.append({"file": filename, "scenario": description,
                        "score": game.score, "wave": game.wave,
                        "ammo": [b.ammo for b in game.batteries],
                        "interceptors": len(game.interceptors),
                        "cities_alive": sum(c.alive for c in game.cities),
                        "state": game.state})

    def add_missiles(game):
        for target, progress in zip(game.cities[::2], (0.28, 0.48, 0.66)):
            missile = module.Missile(target, 51)
            missile.pos = missile.origin.lerp(target.pos, progress)
            game.missiles.append(missile)

    game = scene()
    add_missiles(game)
    save(game, f"{phase}_01_gameplay.png", "Seeded starting scene with three incoming missiles.")
    game = scene()
    target = (70, 180)
    for _ in range(10):
        game.launch(target)
    for _ in range(240):
        game.update(1 / 60)
    add_missiles(game)
    game.launch(target)
    for _ in range(18):
        game.update(1 / 60)
    expected = 0 if phase == "before" else 1
    assert len(game.interceptors) == expected
    save(game, f"{phase}_02_battery_fallback.png",
         "Ten real launches exhaust the left battery; after they settle, click (70,180) again. "
         + ("Original: no interceptor despite other batteries having ammo." if phase == "before"
            else "Fixed: middle battery fires and its ammo falls to nine."))

    if phase == "after":
        game = scene()
        add_missiles(game)
        for x, progress in zip((160, 320, 480, 640), (0.12, 0.38, 0.62, 0.85)):
            blast = module.Explosion((x, 240))
            blast.age = progress * module.EXPLOSION_TIME
            game.explosions.append(blast)
        save(game, "after_03_explosion_colors.png",
             "Four real Explosion objects at lifetime progress 0.12, 0.38, 0.62 and 0.85.")
        game = scene()
        for city in game.cities[:4]:
            missile = module.Missile(city, 51)
            missile.pos = pygame.Vector2(city.pos)
            game.impact(missile)
        save(game, "after_04_city_warning.png", "Four city impacts trigger the critical two-city warning.")
        game = scene()
        missile = module.Missile(game.cities[0], 51)
        missile.pos = pygame.Vector2(game.cities[0].pos)
        game.impact(missile)
        game.score = 1975
        save(game, "after_05_before_repair.png", "One destroyed city; score set to 1975 for the threshold scenario.")
        # Earn the next 25 points using an actual explosion/missile collision.
        missile = module.Missile(game.cities[1], 51)
        missile.pos = pygame.Vector2(400, 220)
        game.missiles.append(missile)
        blast = module.Explosion(missile.pos)
        blast.age = module.EXPLOSION_TIME / 2
        game.explosions.append(blast)
        game.update(1 / 60)
        game.update(1 / 60)
        assert game.score == 2000 and all(c.alive for c in game.cities)
        save(game, "after_06_city_repaired.png", "A collision earns 25 points, crosses 2000 and rebuilds the city.")
        game = scene()
        for city in game.cities:
            missile = module.Missile(city, 51)
            missile.pos = pygame.Vector2(city.pos)
            game.impact(missile)
        save(game, "after_07_game_over.png", "Impacts destroy all six cities and end the game.")
        game.reset()
        save(game, "after_08_reset.png", "Reset restores six cities, full ammunition, score zero and wave one.")
    pygame.quit()
    (ROOT / "screenshots" / f"{phase}_scenarios.json").write_text(json.dumps(records, indent=2) + "\n")
    print(json.dumps(records, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "game.py")
    parser.add_argument("--phase", choices=("before", "after"), required=True)
    args = parser.parse_args()
    capture(args.source, args.phase)
