bl_info = {
  "version": "0.1",
  "name": "Tutorial Maker",
  'author': 'Bob',
  "location": "Properties > Scene",
  "category": "Blender Experiments"
  }


html = """
<!DOCTYPE html>
<html style="height: 100%">

<head>
<style>

/* CSS from the menu example */

div.scrollmenu {
    background-color: #333;
    overflow: auto;
    white-space: nowrap;
    position:absolute;
    bottom: 0px;
    width: 100%;
}

div.scrollmenu a {
    display: inline-block;
    color: white;
    text-align: center;
    padding: 4px;
    text-decoration: none;
}

div.scrollmenu a:hover {
    background-color: #777;
}

/* CSS from the slideshow example */

body {
  font-family: Arial;
  background-color: #000;
  margin: 0;
}

* {
  box-sizing: border-box;
}

img {
  vertical-align: middle;
}

/* Position the image container (needed to position the left and right arrows) */
.container {

  height:100%;
}

/* Hide the images by default */
.mySlides {
  display: none;
}

/* Add a pointer when hovering over the thumbnail images */
.cursor {
  cursor: pointer;
}

/* Next & previous buttons */
.prev,
.next {
  position: absolute;
  top: 0%;
  width: 50%;
  height: 80%;
  padding: 16px;
  margin-top: -50px;
  color: white;
  font-weight: bold;
  font-size: 200px;
  border-radius: 0 3px 3px 0;
  user-select: none;
  -webkit-user-select: none;
}

.prev {
  cursor: w-resize;
}
.next {
  cursor: e-resize;
}

/* Position the "next button" to the right */
.next {
  right: 0;
  border-radius: 3px 0 0 3px;
}

/* On hover, add a black background color with a little bit see-through */
.prev:hover,
.next:hover {
  background-color: rgba(0, 0, 0, 0.1);
}

/* Number text (1/3 etc) */
.numbertext {
  color: #f2f2f2;
  font-size: 12px;
  padding: 8px 12px;
  position: absolute;
  top: 0;
}

/* Container for image text */
.caption-container {
  text-align: center;
  background-color: #222;
  padding: 2px 16px;
  font-size: 18px;
  font-weight: bold;
  color: #ff8;
}

.row:after {
  content: "";
  display: table;
  clear: both;
}

.image-container {
  width:100%;
}

/* N columns side by side */
.column {
  float: left;
  width: 20.0%;  /* This must be 100/#ActualSlides */
}

/* Add a transparency effect for thumnbail images */
.demo {
  opacity: 0.6;
  cursor: pointer;
}

.active,
.demo:hover {
  opacity: 1;
  cursor: pointer;
}


</style>
</head>

<body>

<h1 style="text-align:center;color:#fff;">Demonstration Model</h1>

<div class="container">

  <a class="prev" onclick="plusSlides(-1)"><img src="single_pixel.png"></a>
  <a class="next" onclick="plusSlides(1)"><img src="single_pixel.png"></a>

  <div class="mySlides"> <div class="numbertext">&nbsp; </div> <img class="image-container" src="images/Introduction.png"> </div>
  <div class="mySlides"> <div class="numbertext">&nbsp; </div> <img class="image-container" src="images/Start_with_fresh_install_of_cellblender.png"> </div>
  <div class="mySlides"> <div class="numbertext">&nbsp; </div> <img class="image-container" src="images/Click_Molecules_button.png"> </div>
  <div class="mySlides"> <div class="numbertext">&nbsp; </div> <img class="image-container" src="images/Click_plus_to_create_a_molecule_type.png"> </div>
  <div class="mySlides"> <div class="numbertext">&nbsp; </div> <img class="image-container" src="images/Type_the_molecule_name_red.png"> </div>
  <div class="mySlides"> <div class="numbertext">&nbsp; </div> <img class="image-container" src="images/Type_diffusion_constant_1e-6_for_red.png"> </div>
  <div class="mySlides"> <div class="numbertext">&nbsp; </div> <img class="image-container" src="images/Click_Molecule_Placement.png"> </div>
  <div class="mySlides"> <div class="numbertext">&nbsp; </div> <img class="image-container" src="images/Click_plus_to_release_red_molecules.png"> </div>
  <div class="mySlides"> <div class="numbertext">&nbsp; </div> <img class="image-container" src="images/Click_Molecule_and_select_red.png"> </div>
  <div class="mySlides"> <div class="numbertext">&nbsp; </div> <img class="image-container" src="images/Type_1_in_Site_Diameter_Field.png"> </div>
  <div class="mySlides"> <div class="numbertext">&nbsp; </div> <img class="image-container" src="images/Type_1000_in_Quantity_to_Release_Field.png"> </div>
  <div class="mySlides"> <div class="numbertext">&nbsp; </div> <img class="image-container" src="images/Click_Run_Simulation_Panel_button.png"> </div>
  <div class="mySlides"> <div class="numbertext">&nbsp; </div> <img class="image-container" src="images/Click_File_Save_As_to_save.png"> </div>
  <div class="mySlides"> <div class="numbertext">&nbsp; </div> <img class="image-container" src="images/Type_file_name_my_model.png"> </div>
  <div class="mySlides"> <div class="numbertext">&nbsp; </div> <img class="image-container" src="images/Click_Save_As_Blender_File.png"> </div>
  <div class="mySlides"> <div class="numbertext">&nbsp; </div> <img class="image-container" src="images/Click_Export_and_Run_button.png"> </div>
  <div class="mySlides"> <div class="numbertext">&nbsp; </div> <img class="image-container" src="images/Click_Reload_Visualization.png"> </div>
  <div class="mySlides"> <div class="numbertext">&nbsp; </div> <img class="image-container" src="images/Special_Drag_time_line_0.png"> </div>
  <div class="mySlides"> <div class="numbertext">&nbsp; </div> <img class="image-container" src="images/Special_Drag_time_line_50.png"> </div>
  <div class="mySlides"> <div class="numbertext">&nbsp; </div> <img class="image-container" src="images/Special_Drag_time_line_200.png"> </div>
  <div class="mySlides"> <div class="numbertext">&nbsp; </div> <img class="image-container" src="images/Special_Drag_time_line_700.png"> </div>
  <div class="mySlides"> <div class="numbertext">&nbsp; </div> <img class="image-container" src="images/Click_Molecules_button_2.png"> </div>
  <div class="mySlides"> <div class="numbertext">&nbsp; </div> <img class="image-container" src="images/Click_Display_Options.png"> </div>
  <div class="mySlides"> <div class="numbertext">&nbsp; </div> <img class="image-container" src="images/Type_Scale_Factor_to_3.0.png"> </div>
  <div class="mySlides"> <div class="numbertext">&nbsp; </div> <img class="image-container" src="images/Click_plus_to_add_a_second_molecule_type.png"> </div>
  <div class="mySlides"> <div class="numbertext">&nbsp; </div> <img class="image-container" src="images/Type_Change_molecule_name_to_green.png"> </div>
  <div class="mySlides"> <div class="numbertext">&nbsp; </div> <img class="image-container" src="images/Type_Change_Diffusion_Constant_to_1e-5.png"> </div>
  <div class="mySlides"> <div class="numbertext">&nbsp; </div> <img class="image-container" src="images/Change_Scale_Factor_to_3.0.png"> </div>
  <div class="mySlides"> <div class="numbertext">&nbsp; </div> <img class="image-container" src="images/Click_Molecule_Placement_button.png"> </div>
  <div class="mySlides"> <div class="numbertext">&nbsp; </div> <img class="image-container" src="images/Click_Plus_to_add_second_release_site.png"> </div>
  <div class="mySlides"> <div class="numbertext">&nbsp; </div> <img class="image-container" src="images/Change_Molecule_to_green.png"> </div>
  <div class="mySlides"> <div class="numbertext">&nbsp; </div> <img class="image-container" src="images/Type_Change_Y_Location_to_0.5.png"> </div>
  <div class="mySlides"> <div class="numbertext">&nbsp; </div> <img class="image-container" src="images/Type_Quantity_to_Release_900.png"> </div>
  <div class="mySlides"> <div class="numbertext">&nbsp; </div> <img class="image-container" src="images/Click_Run_Simulation_button.png"> </div>
  <div class="mySlides"> <div class="numbertext">&nbsp; </div> <img class="image-container" src="images/Click_Export_and_Run_button_again.png"> </div>
  <div class="mySlides"> <div class="numbertext">&nbsp; </div> <img class="image-container" src="images/Click_Reload_Viz_Data_for_green.png"> </div>
  <div class="mySlides"> <div class="numbertext">&nbsp; </div> <img class="image-container" src="images/Conclusion.png"> </div>

  <div class="caption-container">
    <h2><p id="caption"></p></h2>
  </div>


</div>


<script>
var slideIndex = 1;
showSlides(slideIndex,true);

function plusSlides(n) {
  // plusSlides is called without clicking an icon directly. Scroll to show active.
  showSlides(slideIndex+=n,true);
}

function currentSlide(n) {
  // currentSlide is called when an icon is clicked directly. Don't move it in this case.
  showSlides(slideIndex=n,false);
}

function showSlides(n,scroll) {
  var i;
  var slides = document.getElementsByClassName("mySlides");
  var icons = document.getElementsByClassName("icon");
  var captionText = document.getElementById("caption");

  // Ensure the slideIndex is within range
  if (n > slides.length) {
    slideIndex = 1;
  }
  if (n < 1) {
    slideIndex = slides.length;
  }
  // Hide all of the slides
  for (i = 0; i < slides.length; i++) {
    slides[i].style.display = "none";
  }
  // Remove the "active" property from all icons
  for (i = 0; i < icons.length; i++) {
    icons[i].className = icons[i].className.replace(" active", "");
  }
  // Show the selected slide
  slides[slideIndex-1].style.display = "block";
  // Make the selected icon active
  if (slideIndex-1 < icons.length ) {
    icons[slideIndex-1].className += " active";
  }
  // If scroll was requested, set the scrollbar to show the icon for the current image
  if (scroll) {
    sb = document.getElementById("icon_bar");
    // sb.scrollWidth is the width of all of the child items put together
    // sb.getBoundingClientRect.width is the width of the window in which to fit the visible portion of sb.scrollWidth
    slide_width = sb.scrollWidth / slides.length
    scrollbar_width = sb.getBoundingClientRect().width
    sb.scrollLeft = ( slide_width * (slideIndex-1) ) + (slide_width/2) - (scrollbar_width / 2)
  }
  // Set the caption based on the "alt" text for each icon
  if (slideIndex <= icons.length) {
    captionText.innerHTML = icons[slideIndex-1].alt;
  } else {
    captionText.innerHTML = " &nbsp; ";
  }
}
</script>

<div class="scrollmenu" id="icon_bar">
    <img class="icon demo" src="images/Introduction.png" width="300" onclick="currentSlide(1)" alt="Introduction">
    <img class="icon demo" src="images/Start_with_fresh_install_of_cellblender.png" width="300" onclick="currentSlide(2)" alt="Start: &nbsp; Empty Model">
    <img class="icon demo" src="images/Click_Molecules_button.png" width="300" onclick="currentSlide(3)" alt="Click: &nbsp; Open Molecules Panel">
    <img class="icon demo" src="images/Click_plus_to_create_a_molecule_type.png" width="300" onclick="currentSlide(4)" alt="Click: &nbsp; Plus button to create a molecule">
    <img class="icon demo" src="images/Type_the_molecule_name_red.png" width="300" onclick="currentSlide(5)" alt="Type: &nbsp; 'red' to name the molecule">
    <img class="icon demo" src="images/Type_diffusion_constant_1e-6_for_red.png" width="300" onclick="currentSlide(6)" alt="Type: &nbsp; Diffusion constant: 1e-6">
    <img class="icon demo" src="images/Click_Molecule_Placement.png" width="300" onclick="currentSlide(7)" alt="Click: &nbsp; Open Molecule Placement Panel">
    <img class="icon demo" src="images/Click_plus_to_release_red_molecules.png" width="300" onclick="currentSlide(8)" alt="Click: &nbsp; Plus button to add a release site">
    <img class="icon demo" src="images/Click_Molecule_and_select_red.png" width="300" onclick="currentSlide(9)" alt="Click: &nbsp; Select 'red' molecule to release">
    <img class="icon demo" src="images/Type_1_in_Site_Diameter_Field.png" width="300" onclick="currentSlide(10)" alt="Type: &nbsp; Site Diameter of 1">
    <img class="icon demo" src="images/Type_1000_in_Quantity_to_Release_Field.png" width="300" onclick="currentSlide(11)" alt="Type: &nbsp; Quantity to Release of 1000">
    <img class="icon demo" src="images/Click_Run_Simulation_Panel_button.png" width="300" onclick="currentSlide(12)" alt="Click: &nbsp; Run Simulation button">
    <img class="icon demo" src="images/Click_File_Save_As_to_save.png" width="300" onclick="currentSlide(13)" alt="Menu: &nbsp; File / Save As...">
    <img class="icon demo" src="images/Type_file_name_my_model.png" width="300" onclick="currentSlide(14)" alt="Type: &nbsp; File name of 'my_model.blend'">
    <img class="icon demo" src="images/Click_Save_As_Blender_File.png" width="300" onclick="currentSlide(15)" alt="Click: &nbsp; Save As Blender File">
    <img class="icon demo" src="images/Click_Export_and_Run_button.png" width="300" onclick="currentSlide(16)" alt="Click: &nbsp; Export & Run">
    <img class="icon demo" src="images/Click_Reload_Visualization.png" width="300" onclick="currentSlide(17)" alt="Click: &nbsp; Reload Visualization Data">
    <img class="icon demo" src="images/Special_Drag_time_line_0.png" width="300" onclick="currentSlide(18)" alt="Special: &nbsp; Zoom in with mouse wheel">
    <img class="icon demo" src="images/Special_Drag_time_line_50.png" width="300" onclick="currentSlide(19)" alt="Click: &nbsp; Click on time line around 50">
    <img class="icon demo" src="images/Special_Drag_time_line_200.png" width="300" onclick="currentSlide(20)" alt="Click: &nbsp; Click on time line around 200">
    <img class="icon demo" src="images/Special_Drag_time_line_700.png" width="300" onclick="currentSlide(21)" alt="Click: &nbsp; Click on time line around 700">
    <img class="icon demo" src="images/Click_Molecules_button_2.png" width="300" onclick="currentSlide(22)" alt="Click: &nbsp; Open Molecules Panel">
    <img class="icon demo" src="images/Click_Display_Options.png" width="300" onclick="currentSlide(23)" alt="Click: &nbsp; Open Display Options">
    <img class="icon demo" src="images/Type_Scale_Factor_to_3.0.png" width="300" onclick="currentSlide(24)" alt="Type: &nbsp; Change Scale Factor to 3">
    <img class="icon demo" src="images/Click_plus_to_add_a_second_molecule_type.png" width="300" onclick="currentSlide(25)" alt="Click: &nbsp; Plus button to add another molecule">
    <img class="icon demo" src="images/Type_Change_molecule_name_to_green.png" width="300" onclick="currentSlide(26)" alt="Type: &nbsp; Change new molecule name to 'green'">
    <img class="icon demo" src="images/Type_Change_Diffusion_Constant_to_1e-5.png" width="300" onclick="currentSlide(27)" alt="Type: &nbsp; Diffusion constant: 1e-5">
    <img class="icon demo" src="images/Change_Scale_Factor_to_3.0.png" width="300" onclick="currentSlide(28)" alt="Type: &nbsp; Scale Factor 3.0">
    <img class="icon demo" src="images/Click_Molecule_Placement_button.png" width="300" onclick="currentSlide(29)" alt="Click: &nbsp; Molecule Placement button">
    <img class="icon demo" src="images/Click_Plus_to_add_second_release_site.png" width="300" onclick="currentSlide(30)" alt="Click: &nbsp; Plus button to add a release site">
    <img class="icon demo" src="images/Change_Molecule_to_green.png" width="300" onclick="currentSlide(31)" alt="Click: &nbsp; Select the 'green' to release">
    <img class="icon demo" src="images/Type_Change_Y_Location_to_0.5.png" width="300" onclick="currentSlide(32)" alt="Type: &nbsp; 0.5 to release at y=0.5">
    <img class="icon demo" src="images/Type_Quantity_to_Release_900.png" width="300" onclick="currentSlide(33)" alt="Type: &nbsp; 900 to release 900 molecules">
    <img class="icon demo" src="images/Click_Run_Simulation_button.png" width="300" onclick="currentSlide(34)" alt="Click: &nbsp; Run Simulation button to open panel">
    <img class="icon demo" src="images/Click_Export_and_Run_button_again.png" width="300" onclick="currentSlide(35)" alt="Click: &nbsp; 'Export & Run' to run another simulation">
    <img class="icon demo" src="images/Click_Reload_Viz_Data_for_green.png" width="300" onclick="currentSlide(36)" alt="Click: &nbsp; Reload Visualization Data">
    <img class="icon demo" src="images/Conclusion.png" width="300" onclick="currentSlide(37)" alt="Conclusion">
  </div>

</body>
</html>

"""

has_blender = False
try:
  import bpy
  has_blender = True
except:
  pass

if has_blender:
  from bpy.props import *

  class CREATE_OT_tutorial(bpy.types.Operator):
      """Process actions after a delay so the screen can respond to commands"""
      bl_idname = "create.tutorial"
      bl_label = "Create Tutorial Slides"
      bl_options = {'REGISTER'}

      _timer = None
      _count = 0

      def modal(self, context, event):
          if event.type == 'TIMER':
              print ( "Timer event with _count = " + str(self._count) )

              if self._count > 0:

                  fname = "tutorial_maker_image_" + str(self._count) + ".png"
                  print ( "Saving file: " + fname )
                  alt_context = {
                      'region'  : None,
                      'area'    : None,
                      'window'  : bpy.context.window,
                      'scene'   : bpy.context.scene,
                      'screen'  : bpy.context.window.screen
                  }
                  bpy.ops.screen.screenshot(alt_context, filepath=fname, full=True)

                  bpy.data.materials['Material'].diffuse_color[0] = self._count % 2 # red
                  bpy.data.materials['Material'].diffuse_color[1] = (self._count >> 1) % 2 # green
                  bpy.data.materials['Material'].diffuse_color[2] = (self._count >> 2) % 2 # blue
                  # just a silly way of forcing a screen update. ¯\_(ツ)_/¯
                  color = context.user_preferences.themes[0].view_3d.space.gradients.high_gradient
                  color.h += 0.01
                  color.h -= 0.01
                  self._count += -1

              else:

                  self.cancel(context)

          return {'PASS_THROUGH'}

      def execute(self, context):
          print ( "Inside tutorial.execute with context = " + str(context) )
          delay = 2.0
          print ( "Setting timer to delay of " + str(delay) )
          wm = context.window_manager
          self._count = 5
          self._timer = wm.event_timer_add(delay, context.window)
          wm.modal_handler_add(self)
          return {'RUNNING_MODAL'}

      def cancel(self, context):
          wm = context.window_manager
          wm.event_timer_remove(self._timer)


  class CreateTutorialPanel(bpy.types.Panel):
      bl_label = "Create Tutorial"
      bl_space_type = "PROPERTIES"
      bl_region_type = "WINDOW"
      bl_context = "scene"
      def draw(self, context):
          row = self.layout.row()
          row.operator("create.tutorial")

  def register():
      print ("Registering ", __name__)
      bpy.utils.register_module(__name__)

  def unregister():
      print ("Unregistering ", __name__)
      bpy.utils.unregister_module(__name__)

  if __name__ == "__main__":
      print ( "Called as main with Blender" )
      register()

else:

  if __name__ == "__main__":
      print ( "Called as main without Blender" )


