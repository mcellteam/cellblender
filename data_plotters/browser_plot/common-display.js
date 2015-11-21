/**
 * contains functions used by both plot-main.js and histogram.js
 * @author Beilin Li
 */

function updateChartDimensions(chart) {
	var rightElem = $('#outer-expand');
	var rightPos = rightElem.offset().left + rightElem.outerWidth();
	var widthPct = 99.0 - 100.0 * rightPos/$(window).width();
	$('#chart-container').css({ 'width': widthPct + '%' });
	
	chart.setSize($('#chart').width(), $('#chart').height(), false);
}

function initResizable(chart) {
	$('.side-panel').resizable({
		handles: 'e',
		resize: function(event, ui) {
			updateChartDimensions(chart);
		}
	});
	$('#chart-settings').resizable({ handles: 's' });

	$('#chart').resizable({
		handles: 'se',
		resize: function(event, ui) {
			chart.setSize($(this).width(), $(this).height(), false);

			var marginWidth = 50 - (50.0 * $(this).width() / $('#chart-container').width());
			$(this).css({ 'margin-left': marginWidth + '%' });
		},

		/**
		 * keeping CSS property percentage based
		 * to preserve proportionality to the page
		 */
		stop: function(event, ui) {
			var widthPct = 100.0 * $(this).width()/$('#chart-container').width();
			var heightPct = 100.0 * $(this).height()/$('#chart-container').height();
			$(this).css({ 'width': widthPct + '%',
						'height': heightPct + '%' });
		}
	});
}

function showLabelOptions(labelElem, editElem, offsetX, offsetY) {
	console.log(window);
	editElem.visible();
	var pos = $('#chart').offset();
	var x = pos.left + offsetX;
	var y = pos.top + offsetY;
	editElem.position(x, y);
	editElem.children('.label-text')
		.val(labelElem.options.title.text);
	editElem.children('.label-color')
		.val(labelElem.options.title.style.color);
	editElem.children('.label-size')
		.val(parseInt(labelElem.options.title.style.fontSize));
	editElem.children('.label-font')
		.val(labelElem.options.title.style.fontFamily);

	// axis only
	if ((editElem.children('.tick-interval')).length) {
		editElem.children('.tick-interval')
			.val(labelElem.tickInterval);
	}
}

function getLabelElem(chart, eName) {
	switch (eName) {
		case "edit-title": return chart;
		case "edit-x-label": return chart.xAxis[0];
		case "edit-y-label": return chart.yAxis[0]; 
		default: alert("error");
	}
}

/* user options for changing axis/chart titles
 * edit options displayed on label mouseover and
 * hidden on cancel/chart/apply click
 */
function initFonts() {
	var fontList = ['Times New Roman', 'Arial', 'Helvetica', 'Arial Black', 'Comic Sans MS', 'Lucida Grande', 'Tahoma', 'Geneva', 'Verdana', 'Courier New'];

	for (var i = 0; i < fontList.length; i++) {
		$('.edit-label .label-font').append($('<option>')
			.append(fontList[i])
			.attr("name", fontList[i]));
	}
}

function applyLabel(chart, parent) {
	var labelElem = getLabelElem(chart, parent.attr("id"));
	
	var newStyle = {
		color: parent.children('.label-color').val(),
		fontSize: parent.children('.label-size').val() + 'px',
		fontFamily: parent.children('.label-font').val()
	};

	labelElem.setTitle({
		text: parent.children('.label-text').val(),
		style: newStyle
	});

	if (parent.attr("id") !== "edit-title") {
		labelElem.update({
			labels: { style: newStyle },
			tickInterval: parseFloat(parent.children('.tick-interval').val())
		});
	}

	$('.edit-label').invisible();
}

function initLabelOptions(chart) {
	$('.cancel').click(function() {
		$('.edit-label').invisible();
	});

	$('.label-color').spectrum({
		showInput: true,
		preferredFormat: 'hex'
	});

	initFonts();

	$('.apply-label').click(function() {
		console.log($(this).parent());
		applyLabel(chart, $(this).parent());
	});
}
