import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import sys
from pathlib import Path
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pygame
import game


class GameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.screen = pygame.display.set_mode((game.WIDTH, game.HEIGHT))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.g = game.Game()
        self.g.to_spawn, self.g.spawn_timer = 1, 999

    def missile_at(self, target, pos):
        missile = game.Missile(target, 51)
        missile.pos = pygame.Vector2(pos)
        return missile

    def test_closest_available_battery(self):
        self.assertIs(self.g.nearest_battery((70, 180)), self.g.batteries[0])

    def test_empty_battery_falls_back_and_debits_ammo(self):
        self.g.batteries[0].ammo = 0
        self.g.launch((70, 180))
        self.assertEqual([b.ammo for b in self.g.batteries], [0, 9, 10])
        self.assertEqual(self.g.interceptors[0].origin, self.g.batteries[1].pos)

    def test_destroyed_battery_falls_back(self):
        self.g.batteries[0].alive = False
        self.g.launch((70, 180))
        self.assertEqual(self.g.interceptors[0].origin, self.g.batteries[1].pos)

    def test_mixed_unavailable_batteries(self):
        self.g.batteries[0].ammo = 0
        self.g.batteries[1].alive = False
        self.assertIs(self.g.nearest_battery((70, 180)), self.g.batteries[2])

    def test_all_empty_or_dead_is_safe(self):
        for battery in self.g.batteries:
            battery.ammo = 0
        self.assertIsNone(self.g.nearest_battery((400, 100)))
        self.g.launch((400, 100))
        self.assertEqual(self.g.interceptors, [])
        for battery in self.g.batteries:
            battery.ammo, battery.alive = 10, False
        self.g.launch((400, 100))
        self.assertEqual(self.g.interceptors, [])

    def test_cannot_launch_at_ground_or_after_loss(self):
        self.g.launch((100, game.GROUND_Y))
        self.g.state = "lose"
        self.g.launch((100, 100))
        self.assertEqual(self.g.interceptors, [])
        self.assertEqual([b.ammo for b in self.g.batteries], [10, 10, 10])

    def test_interceptor_snaps_to_exact_target_without_early_detonation(self):
        interceptor = game.Interceptor((0, 0), (100, 0))
        self.assertFalse(interceptor.update(0.1))
        self.assertEqual(interceptor.pos, pygame.Vector2(42, 0))
        self.assertFalse(interceptor.update(0.1))
        self.assertTrue(interceptor.update(0.1))
        self.assertEqual(interceptor.pos, interceptor.target)
        # Old code detonated merely because the remaining distance was under six.
        interceptor = game.Interceptor((0, 0), (5, 0))
        self.assertFalse(interceptor.update(0.001))

    def test_zero_distance_interceptor_is_safe(self):
        interceptor = game.Interceptor((4, 4), (4, 4))
        self.assertTrue(interceptor.update(0))

    def test_detonation_explosion_is_at_target(self):
        self.g.interceptors = [game.Interceptor((60, 560), (61, 550))]
        self.g.update(0.05)
        self.assertFalse(self.g.interceptors)
        self.assertEqual(self.g.explosions[0].pos, pygame.Vector2(61, 550))

    def test_explosion_colors_are_valid_and_clamped(self):
        self.assertEqual(game.explosion_color(0), (255, 255, 255))
        self.assertEqual(game.explosion_color(1), (150, 25, 15))
        self.assertEqual(game.explosion_color(-1), game.explosion_color(0))
        self.assertEqual(game.explosion_color(2), game.explosion_color(1))
        colors = [game.explosion_color(i / 100) for i in range(101)]
        self.assertGreater(len(set(colors)), 90)
        self.assertTrue(all(len(c) == 3 and all(type(v) is int and 0 <= v <= 255 for v in c)
                            for c in colors))

    def test_city_destruction_calls_hook_once(self):
        city = self.g.cities[0]
        missile = self.missile_at(city, city.pos)
        with patch.object(game, "on_city_destroyed", wraps=game.on_city_destroyed) as hook:
            self.g.impact(missile)
            self.g.impact(missile)
            hook.assert_called_once_with(city)
        self.assertFalse(city.alive)
        self.assertEqual(city.alert_time, 3)

    def test_battery_impact_does_not_call_city_hook(self):
        battery = self.g.batteries[0]
        with patch.object(game, "on_city_destroyed") as hook:
            self.g.impact(self.missile_at(battery, battery.pos))
            hook.assert_not_called()
        self.assertFalse(battery.alive)

    def test_city_alert_expires(self):
        game.on_city_destroyed(self.g.cities[0])
        self.g.update(3.1)
        self.assertEqual(self.g.cities[0].alert_time, 0)

    def test_repair_threshold_and_once_per_milestone(self):
        self.assertEqual(game.city_repair_threshold(), 2000)
        self.g.cities[0].alive = False
        self.g.score = 1999
        self.g.update(0)
        self.assertFalse(self.g.cities[0].alive)
        self.g.score = 2000
        self.g.update(0)
        self.assertTrue(self.g.cities[0].alive)
        self.assertEqual(self.g.repairs_awarded, 1)
        self.g.cities[0].alive = False
        self.g.update(0)
        self.assertFalse(self.g.cities[0].alive)
        self.g.score = 4000
        self.g.update(0)
        self.assertTrue(self.g.cities[0].alive)
        self.assertEqual(self.g.repairs_awarded, 2)

    def test_score_jump_awards_each_crossed_milestone(self):
        for city in self.g.cities[:3]:
            city.alive = False
        self.g.score = 6000
        self.g.update(0)
        self.assertTrue(all(c.alive for c in self.g.cities))
        self.assertEqual(self.g.repairs_awarded, 3)

    def test_no_destroyed_city_does_not_bank_repair(self):
        self.g.score = 2000
        self.g.update(0)
        self.g.cities[0].alive = False
        self.g.update(0)
        self.assertFalse(self.g.cities[0].alive)

    def test_repair_can_be_disabled(self):
        self.g.cities[0].alive = False
        self.g.score = 2000
        with patch.object(game, "city_repair_threshold", return_value=None):
            self.g.update(0)
            self.g.draw(self.screen)
        self.assertFalse(self.g.cities[0].alive)

    def test_collision_scores_once_in_overlapping_blasts(self):
        self.g.missiles = [self.missile_at(self.g.cities[0], (300, 200)),
                           self.missile_at(self.g.cities[1], (500, 200))]
        for _ in range(2):
            blast = game.Explosion((300, 200))
            blast.age = game.EXPLOSION_TIME / 2
            self.g.explosions.append(blast)
        self.g.update(0)
        self.assertEqual(self.g.score, 25)
        self.assertEqual(len(self.g.missiles), 1)
        self.assertEqual(self.g.missiles[0].pos, pygame.Vector2(500, 200))

    def test_blast_boundary_counts_as_collision(self):
        blast = game.Explosion((300, 200))
        blast.age = game.EXPLOSION_TIME / 2
        self.g.explosions = [blast]
        self.g.missiles = [self.missile_at(self.g.cities[0], (345, 200))]
        self.g.update(0)
        self.assertEqual(self.g.score, 25)

    def test_expired_blast_cannot_score(self):
        blast = game.Explosion((300, 200))
        blast.age = game.EXPLOSION_TIME
        self.g.explosions = [blast]
        self.g.missiles = [self.missile_at(self.g.cities[0], (300, 200))]
        self.g.update(0.05)
        self.assertEqual(self.g.score, 0)
        self.assertEqual(len(self.g.missiles), 1)
        self.assertEqual(self.g.explosions, [])

    def test_unintercepted_missile_destroys_target(self):
        city = self.g.cities[0]
        self.g.missiles = [self.missile_at(city, (city.pos.x, game.GROUND_Y - 3))]
        self.g.update(0)
        self.assertFalse(city.alive)
        self.assertFalse(self.g.missiles)

    def test_wave_waits_for_flying_interceptor(self):
        self.g.to_spawn = 0
        self.g.launch((400, 100))
        self.g.update(0.01)
        self.assertEqual(self.g.wave, 1)
        self.assertEqual(len(self.g.interceptors), 1)

    def test_wave_bonus_and_replenishment(self):
        self.g.to_spawn = 0
        self.g.batteries[0].ammo = 0
        self.g.batteries[1].alive = False
        self.g.update(0)
        self.assertEqual(self.g.wave, 2)
        self.assertEqual(self.g.score, 700)
        self.assertTrue(all(b.alive and b.ammo == 10 for b in self.g.batteries))

    def test_spawn_avoids_destroyed_targets(self):
        for city in self.g.cities:
            city.alive = False
        for battery in self.g.batteries[:2]:
            battery.alive = False
        self.g.spawn_missile()
        self.assertIs(self.g.missiles[0].target, self.g.batteries[2])

    def test_loss_and_reset(self):
        for city in self.g.cities:
            self.g.impact(self.missile_at(city, city.pos))
        self.assertEqual(self.g.state, "lose")
        self.g.update(0.05)
        self.g.draw(self.screen)
        self.g.reset()
        self.assertEqual((self.g.score, self.g.wave, self.g.state, self.g.repairs_awarded),
                         (0, 1, "play", 0))
        self.assertTrue(all(c.alive and c.alert_time == 0 for c in self.g.cities))
        self.assertTrue(all(b.alive and b.ammo == 10 for b in self.g.batteries))
        self.assertFalse(self.g.explosions or self.g.interceptors or self.g.missiles)

    def test_real_main_loop_handles_click_reset_and_quit(self):
        batches = [[pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(80, 120))],
                   [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r)],
                   [pygame.event.Event(pygame.QUIT)]]
        with patch.object(pygame.event, "get", side_effect=batches), \
                patch.object(game.Game, "launch", autospec=True, wraps=None) as launch, \
                patch.object(game.Game, "reset", autospec=True, side_effect=game.Game.reset) as reset:
            game.main()
            launch.assert_called_once()
            self.assertEqual(launch.call_args.args[1], (80, 120))
            self.assertEqual(reset.call_count, 2)  # Initial construction plus R.
        pygame.init()
        self.__class__.screen = pygame.display.set_mode((game.WIDTH, game.HEIGHT))


if __name__ == "__main__":
    unittest.main(verbosity=2)
