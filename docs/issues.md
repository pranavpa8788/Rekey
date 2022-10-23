# Issues

## Known Issues

These are some of the known issues/bugs and will be soon fixed in the coming updates.

- Images get clipped when fit_to_image is set to false

	Description: A zoom in/zoom out keybinding feature should fix this issue where the images could start from the most zoomed out view

- Parameter checks

	Description: Errors are expected if you specify invalid types as there are no limit and type checks within the program yet

	Example: window_position_x: 50% (Fix: should be enclosed within quotes as "50%")

- Moving to the immediate child node of current node

	Description: The way the current navigation mode works is, the node position defaults to 0 when moving up or down levels. Hence the ability to move to immediate child nodes is not available yet

- Arrow keys not working

	Description: The GlobalHotKeys function from pynput is not able to detect arrow keys for some reason (at least on my computer). This function will be replaced by individual key listeners in the future

## Upcoming features

Do read the [upcoming features page](https://github.com/pranavpa8788/Rekey/blob/main/docs/more_info.md) before creating feature requests

## Issue format

Make sure to include the following parameters when reporting issues (in any order)

- Issue info

	Description: Detail description of issue

- Python version

	Description: Version of python you are using to run the program

	Command: `python --version`

- Config file

	Description: A copy of either you config.json file or all the parameters relevant to the issue

- Pip version

	Description: Version of python package manager pip

	Command: `pip --version`

- OS

	Description: Your operating system along with its version

- Module versions

	Description: Version of [PyQt5], [pynput], [Pillow]

	Command: `pip show package_name`
