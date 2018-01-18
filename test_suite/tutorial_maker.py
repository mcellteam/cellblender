f = open ( "tutorial_list.txt", 'r' )

txt = f.read() + "  ]\n}\n"

tut = eval(txt)

html = open ( "tutorial.html", 'w' )


top_html = """
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

"""

html.write ( top_html )

for frame in tut['frames']:

  html.write ( '<div class="mySlides"> <div class="numbertext">&nbsp; </div> <img class="image-container" src="' + frame['fname'] + '"> </div>' )

mid_html = """

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
"""

html.write ( mid_html )

i = 1
for frame in tut['frames']:
  html.write ( '<img class="icon demo" src="' + frame['fname'] + '" width="300" onclick="currentSlide(' + str(i) + ')" alt="' + frame['desc'] + '">' )
  i += 1


bot_html = """
  </div>

</body>
</html>
"""

html.write ( bot_html )

