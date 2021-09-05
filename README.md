Tile Map Editor
---
Creates a JSON file containing locations and names of tiles in a world.

Usage
---
Input source images into the "./imgs" folder. These images MUST have unique names, as these names are saved in the JSON output and used to load the map for future editing.

### Prerequisites: 
    - Python 3
    - Pygame
### To Run:
1. Open a terminal and cd into the root project folder. (`cd /path/to/tilemapeditor`)
2. Run the `main.py` script with python (`python3 main.py -i <input file (opt)> <output filename>`)

##### Controls:
> Keys 1-9: Select image from palette 
> 
> Move: WASD/Arrow Keys
> 
> Paint: Left click
> 
> Save tilemap: G
> 
> Erase mode: E
> 
> Pen mode: P
> 
> Zoom In: EQUALS
> 
> Zoom Out: MINUS
> 
> Exit: ESCAPE
> 
> Layer up: ]
> 
> Layer down: [
