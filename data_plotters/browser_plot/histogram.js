(function($) {
    $.fn.invisible = function() {
        return this.each(function() {
            $(this).css("display", "none");
        });
    };
    $.fn.visible = function() {
        return this.each(function() {
            $(this).css("display", "block");
        });
    };

	$.fn.hidden = function() {
		return $(this).css("display") === "none";
	}

	$.fn.position = function(x, y) {
		$(this).css("top", y + "px");
		$(this).css("left", x + "px");
	}
}(jQuery));

var chart,
	origSeries, // determined in plot-main.js
	dataMax,
	dataMin,
	binCount,
	binSize;

(function() {
	$(window).load(function () {
		initChart();
		chartDisplayOptions();
		initLabelOptions(chart);
		initResizable(chart);
		initExpandable();
	});

	function initChart() {
		initChartOptions();
		initHistOptions();
		updateCategories();
		updateSeries();
	}

	function initChartOptions() {
		chart = new Highcharts.Chart({
			chart: {
				renderTo: 'chart',
				type: 'column',			
				zoomType: 'xy'
			},
			credits: { enabled: false },
			title: {
				useHTML: true,
				margin: 30,
				text: 'Reaction Data',
				events: {
					click: function() {
						showLabelOptions(this, $('#edit-title'), this.title.x, this.title.y);
					}
				},
				style: {
					fontFamily: 'Lucida Grande',
					fontSize: '18px'
				}
			},

			xAxis: {
				labels: {
					style: { fontSize: '12px', fontFamily: 'Lucida Grande' }
				},
				title: {
					events: {
						click: function() {
							showLabelOptions(this, $('#edit-x-label'), this.chart.chartWidth/2.0, this.chart.chartHeight - 60);
						}
					},

					style: { fontSize: '12px', fontFamily: 'Lucida Grande' },
				}
			},
			
			yAxis: {
				labels: {
					style: { fontSize: '12px', fontFamily: 'Lucida Grande' }
				},
				title: {
					events: {
						click: function() {
							showLabelOptions(this, $('#edit-y-label'), 20, this.chart.chartHeight/2.0 - 20);
						}
					},

					style: { fontSize: '12px', fontFamily: 'Lucida Grande' }
				}
			}
		});
	}

	function initHistOptions() {
		dataMax = dataMin = null;
		$.each(origSeries, function(_, series) {
			$.each(series.data, function(_, pt) {
				if (dataMax === null) {
					dataMax = dataMin = pt.y;
				} else {
					dataMin = Math.min(dataMin, pt.y);
					dataMax = Math.max(dataMax, pt.y);
				}
			});
		});

		binCount = 10;
		binSize = Math.floor((dataMax - dataMin)/binCount) + 1;
	}

	function updateCategories() {
		var categories = new Array();
		for (var i = 0; i < binCount; i++) {
			var xMin = dataMin + i * binSize;
			var xMax = Math.min(xMin + binSize - 1, dataMax);
			categories.push(xMin + " - " + xMax);
		}
		chart.xAxis[0].setCategories(categories);
	}

	function updateHistOptions() {
		binSize = Math.floor((dataMax - dataMin)/binCount) + 1;
	}

	function updateSeries() {
		$.each(origSeries, function(_, series) {
			var seriesData = new Array();
			for (var i = 0; i < binCount; i++) seriesData.push(0);
			$.each(series.data, function(_, pt) {
				var binIndex = Math.floor((pt.y - dataMin)/binSize);
				seriesData[binIndex]++;
			});

			if (chart.get(series.name)) {
				chart.get(series.name).update({ data: seriesData });
			} else {
				chart.addSeries({
					id: series.name,
					name: series.name,
					data: seriesData
				});
			}
		});
	}

	/**
	 * various chart display functions follow
	 */

	/* user options for changing plot range/display */
	function chartDisplayOptions() {
		var curBackground = chart.options.chart.backgroundColor;
	
		$('#chart-color').spectrum({
			color: curBackground,
			showInput: true,
			preferredFormat: 'hex'
		});

		$('#chart-color').val(curBackground);
		$('#chart-color').change(function() {
			chart.chartBackground.css({
				color: $('#chart-color').val()
			});
			$('#chart').css("background", $('#chart-color').val());
		});

		$('#toggle-legend').click(function() {
			var e = $('#toggle-legend');
			if (e.prop("checked"))
				$('.highcharts-legend').visible();
			else
				$('.highcharts-legend').invisible();
		});

		$('#bin-count').val(binCount);
		$('#bin-count').change(function() {
			binCount = $('#bin-count').val();
			updateHistOptions();
			updateCategories();
			updateSeries();
		});
	}

	function initExpandable() {
		$('#outer-expand').click(function() {
			if ($(this).children('span').html() == '\u21fd') {
				$(this).children('span').html('&#x21fe');
			} else {
				$(this).children('span').html('&#x21fd');
			}

			$('#settings-panel').toggle('slide', 50, function() {
				updateChartDimensions(chart);
			});
		});
	}
})();
