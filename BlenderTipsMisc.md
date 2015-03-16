# Blender Tips (Misc) #

These are just an odd collection of tips (miscellaneous). If groups of these tips start to fall into categories, then they can be moved to new wiki pages with more specific names like "BlenderTipsConsole".


---



# Console Tips #

> 
---

> ### Changing the amount of Console Scrollback ###

> The default scrolling window is fairly small, and using commands like: `help (bpy.types.Object)` can easily scroll off the screen.

> To increase the scrolling buffer, go to **"File" / "User Preferences..."** which brings up a dialog box. Select the **"System"** tab at the top, and look in the upper left corner where it says **"General"**. The third item down is titled **"Console Scrollback"** and it allows you to change the amount of scrolling history in the console. Be sure to click the **"Save As Default"** button in the lower left corner if you want that setting to be retained when you restart Blender.

> 
---

> ### Setting tab for autocomplete ###

> The default autocomplete hot key for Blender is "Control-space". This is different from the typical Linux console which uses "tab". Unfortunately, tab is often used to code continuation lines in the Python console, so using tab for autocompletion has its disadvantages. However, if you want to do it for various reasons (like exploring the Blender API), it can be done as follows:

> Go to **"File" / "User Preferences..."** which brings up a dialog box. Select the **"Input"** tab at the top, and expand the "**Console**' tree element. Then uncheck the "**Indent**" action to disable the use of tab for that functionality. Then expand the "**Console Autocomplete**" tree element and click the hot key button (defaulted to "**Ctrl Tab**"). Then type the key combination you want for autocomplete ("**tab**" in this case). Click the "**Save As Default**" button (lower left) to make it the current default. Remember to change it back if you're going to do any command line coding that requires indentation!!


---
