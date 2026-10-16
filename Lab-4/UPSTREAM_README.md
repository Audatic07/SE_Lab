# Missile Command Repair Lab

This project is a single-file Missile Command-lite clone using **Pygame**. It introduces students to click-to-target interception, radius-based collision, and wave-based resource management using a small, readable object-oriented codebase.

---

## What's Provided

A working Missile Command-lite game with:

- Three ground batteries, each with limited ammunition, that fire interceptors toward a clicked point
- Incoming missiles that target cities or batteries and explode into growing/shrinking blast radii on impact or interceptor detonation
- Six cities to defend, wave-based missile counts, and scoring for each missile destroyed

It has **one deliberate bug** and **three optional features** left as empty functions. You are expected to **analyze**, **interact with an AI assistant**, and **complete/fix** the game to make it fully functional and more interesting.

### **Use an LLM (e.g. ChatGPT or Claude) as your debugging and pair-programming partner for this lab.**

---

## Getting Started

### Setup

1. Make sure you have Python 3.10+ installed.
2. Install dependencies:

```bash
pip install pygame
```

3. Run the game:

```bash
python game.py
```

**Controls:** Click anywhere above the ground to launch an interceptor from a battery, `R` to reset.

---

## Tasks to Complete

Each task must be completed using an iterative process involving LLM suggestions and your critical code review.

### Task 1: Fix the battery selection bug

> Clicking near a battery that's already out of ammunition (or destroyed) is supposed to fall back to a different battery that still has ammo. In the current build, `nearest_battery` always returns whichever battery is geometrically closest, with no regard for whether it's alive or has ammo left — so a click near a depleted battery silently does nothing while other batteries sit unused with ammo to spare. Fix the selection so it only considers batteries that are alive and have ammo (still preferring the closest one among those).

### Task 2: Implement `explosion_color(progress)`

> Called once per explosion per frame in `draw`, as `color = explosion_color(explosion.progress) or (int(255 * fade), int(200 * fade), 60)`. It receives the explosion's lifetime progress from `0.0` (just detonated) to `1.0` (about to vanish) and should return an `(r, g, b)` color, or `None` to keep the default fading orange. Idea: shift from white-hot at the center of its life toward red as it fades.

### Task 3: Implement `on_city_destroyed(city)`

> Called from `impact()` the moment a missile destroys a city that was still standing (not for a missile that hits an already-destroyed city, or one that hits a battery). It receives the destroyed `City`. Its return value is ignored. Idea: a screen shake, a warning sound, or a message once few cities remain.

### Task 4: Implement `city_repair_threshold()`

> Called every frame in `update()`. It takes no arguments and should return an integer score value, or `None` to disable city repair entirely. Whenever the score crosses a multiple of that value for the first time, one destroyed city (if any remain destroyed) is rebuilt automatically — the bookkeeping (`self.repairs_awarded`) is already implemented, so you only need to choose the threshold. Idea: return `2000`.

---

## Expected Behavior

- Clicking launches an interceptor from a battery that actually has ammo, toward the clicked point
- Interceptors detonate on arrival at their target, not partway there
- An explosion destroys any incoming missile whose head is within its current blast radius
- A missile that isn't intercepted destroys whatever it was aimed at (city or battery) on impact
- The game ends when every city has been destroyed

---

## Folder Structure

```
missile_command/
├── game.py
└── README.md
```

---

## Submission Checklist

Submission is only the following three things:

- [] A 10-second video of gameplay **before** your changes, showing the bug/broken behavior
- [] A 10-second video of gameplay **after** your changes, showing the bug fixed and the new features working
- [] The Chat/LLM used page link, with the complete chat history
