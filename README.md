# 3D Racing Game (Python / Pygame)

## Description
This is a **3D racing game simulation** built using Python and Pygame.  
The game features:  
- Player-controlled red car  
- AI opponents (blue and green cars)  
- Simple 3D perspective track  
- Obstacles that affect car speed  
- Telemetry display showing lap number and speed  

The player car stays at the bottom of the screen, while AI cars move relative to the player's position, simulating a forward-moving race.

## Features
- Smooth car scaling for depth perception
- Simple AI opponents with acceleration and braking
- Collision with obstacles
- Lap counting system
- Winner detection at the end of the race
- Keyboard controls for player car

## Controls
- **W** – Accelerate  
- **S** – Brake  
- **A** – Move left  
- **D** – Move right  

## Requirements
- Python 3.12+  
- Pygame 2.6+  

Install Pygame using pip if not already installed:  
```bash
pip install pygame
