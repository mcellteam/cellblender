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

(function() {
	var chart;

	var plotFlags = {
		type: 'line',
		marker: null
	}
	
	$(window).load(function () {
		initChart();
		initData();
		initSeriesList();
		chartDisplayOptions();
		initLabelOptions(chart);
		initResizable(chart);
		initExpandable();
		initSpreadsheet();
		otherPlots();
	});
	
	/* window settings */
	$(window).resize(function() {
		triggerSetExtremes();
	});
	
	/* shortcuts for accessing properties of chart state */
	function triggerSetExtremes() {
		var xAxis = chart.xAxis[0];
		var yAxis = chart.yAxis[0];
		xAxis.setExtremes(xAxis.min, xAxis.max);
		yAxis.setExtremes(yAxis.min, yAxis.max);
	}
	
	/**
	 * initial settings
	 */
	function initChart() {
		chart = new Highcharts.Chart({
			chart: {
				events: {
					click: function (e) {
						$('.edit-label').invisible();
					},
					addSeries: triggerSetExtremes
				},
				renderTo: 'chart',
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
				events: {
					afterSetExtremes: function(e) {
						$('#x-min').val(this.min);
						$('#x-max').val(this.max);
					}
				},
				labels: {
					style: { fontSize: '12px', fontFamily: 'Lucida Grande' }
				},
				title: {
					events: {
						click: function() {
							showLabelOptions(this, $('#edit-x-label'), this.chart.chartWidth/2.0, this.chart.chartHeight - 60);
						}
					},
	
					style: { fontSize: '12px', fontFamily: 'Lucida Grande' }
				}
			},
				
			yAxis: {
				events: {
					afterSetExtremes: function(e) {
						$('#y-min').val(this.min);
						$('#y-max').val(this.max);
					}
				},
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
			},
	
			plotOptions: {
				series: {
					animation: false,
					cursor: 'pointer',
					events: {
						click: function (e) {
							// select in sidebar
							var seriesOption = $('#series-list option[name="' + this.name + '"]');
							if (seriesOption.prop("selected")) {
								seriesOption.removeProp("selected");
							} else {
								seriesOption.prop("selected", true);
							}
							$('#series-list').change();

							changeSpreadsheetSeries(this.name);
	                    },
						hide: function(e) {
							triggerSetExtremes();
						},
						remove: function(e) {
							triggerSetExtremes();
						},
						show: function(e) {
							triggerSetExtremes();
						}
	                },
					point: {
						events: {
							click: function() {
								$('#sheet-series-x').val(this.x);
								$('#sheet-series-x').change();
							}
						}
					}
	            }
	        },
		});
	}
	
	/* user options for changing plot range/display */
	function chartDisplayOptions() {
		/* plot options */
		var xAxis = chart.xAxis[0];
		var yAxis = chart.yAxis[0];
	
		$('#x-min').val(xAxis.min);
		$('#x-max').val(xAxis.max);
		$('#y-min').val(yAxis.min);
		$('#y-max').val(yAxis.max);
	
		/* handle input changes */
		$('.plot-range').change(function() {
			xAxis.setExtremes($('#x-min').val(), $('#x-max').val());
			yAxis.setExtremes($('#y-min').val(), $('#y-max').val());
		});
	
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
	
		$('#toggle-ls').click(function() {
			var e = $('#toggle-ls');
			if (e.prop("checked")) plotFlags.type = 'line';
			else plotFlags.type = 'scatter';

			updateAllSeries({ type: plotFlags.type });
		});
	
		$('#mark-type').click(function() {
			var markType = $(this).val();
			if (markType === "true") plotFlags.marker = true;
			else if (markType === "false") plotFlags.marker = false;
			else plotFlags.marker = null;

			updateAllSeries({ marker: { enabled: plotFlags.marker }});
		});
	}

	function initExpandable() {
		function toggleArrow(elem) {
			if (elem.html() == '\u21fd') {
				elem.html('&#x21fe');
			} else {
				elem.html('&#x21fd');
			}
		}

		$('#inner-expand').click(function() {
			toggleArrow($(this).children('span'));
			$('#settings-panel').toggle('slide', 50, function() {
				updateChartDimensions(chart);
			});
		});

		$('#outer-expand').click(function() {
			toggleArrow($(this).children('span'));
			$('#spreadsheet-panel').toggle('slide', 50, function() {	
				updateChartDimensions(chart);
			});
		});
	}

	/***********************************************
		functions for initializing series follow
	***********************************************/
	
	/* receives and parses data from local file and adds to chart
	 * seriesName: desired name of new series
	 * path: path to file
	 */
	
	/* converts file content to array data */
	function parseContent(content) {
		var contentPairs = content.split('\n');
		var dataPairs = new Array();
	
		for (var i = 0; i < contentPairs.length; i++) {
			if (contentPairs[i].length === 0) break;
			var curPair = contentPairs[i].split(' ');
			var x = parseFloat(curPair[0]);
			var y = parseFloat(curPair[1]);
	
			if (isNaN(x) || isNaN(y)) return [];
			dataPairs.push(new Array(x, y));
		}
	
		return dataPairs;
	}
	
	function addSeriesFromPath(seriesName, path) {
		$.ajax({
			type: "GET",
			url: path,
			dataType: 'text',
			success: function(content) {
				var seriesData = parseContent(content);
				chart.addSeries({
					data: seriesData,
					id: seriesName,
					name: seriesName,
					type: plotFlags.type,
					marker: {
						enabled: plotFlags.markerEnabled
					}
				});

				$('#series-list').append($('<option>')
					.append(seriesName)
					.attr("name", seriesName));
			},
			error: function() {
				alert(path + " not found");
			}
		}).done(function() {
			chart.zoom();
		});
	}
	
	
	
	/* read files, add initial series */
	function initData() {
		var plotList;
		$.ajax({
			type: "POST",
			url: 'server.py',
			dataType: 'json',
			data: 'get_plot_specs',
			success: function(content) {	
				plotList = content.plotList;
	
				chart.xAxis[0].setTitle({ text: content.xlabel });
				chart.yAxis[0].setTitle({ text: content.ylabel });
	
				for (var i = 0; i < plotList.length; i++) {
					var fname = plotList[i].fname;
					var title = plotList[i].title;

					addSeriesFromPath(title, fname);
				}
			},
			error: function() {
				alert("error getting file information");
			}
		}).done(function() {
			chart.zoom();
		});
	}
	
	/*********************************************
		functions for series operations follow
	*********************************************/
	
	/* updates all series with the given options */
	function updateAllSeries(options) {
		for (var i = 0; i < chart.series.length; i++)
			chart.series[i].update(options);
	}
	
	/* renames series to newName and replaces relevant options in selection list */
	function renameSeries(series, newName) {
		var prevName = series.name;
		series.update({
			id: newName,
			name: newName
		});
	
		$('#series-name').val(newName);
		$('#series-list option[name="' + prevName + '"]')
			.attr("name", newName)
			.text(newName);

		// reflect in spreadsheet
		if ($('#sheet-title').text() === prevName) {
			$('#sheet-title').text(newName);
		}
	}
	
	
	/* update series data on file change */
	function changeSeriesFromFile() {
		var files = ($('#series-data'))[0].files;
		if (chart.get(files[0].name)) {
			alert("Series with this name already exists.");
			return;
		}
	
		var selectedOption = $('#series-list').val();
		if (selectedOption.length > 1) {
			alert("Multiple series selected!");
			return;
		}
	
		var curSeries = chart.get(selectedOption[0]);
	
		var f = new FileReader();
		f.onload = function(e) {
			var content = e.target.result;
			var seriesData = parseContent(content);
			curSeries.update({ data: seriesData });
			renameSeries(curSeries, files[0].name);
			changeSpreadsheetSeries(files[0].name);
		}
		f.readAsText(files[0]);
	}
	
	function addSeriesFromFile(file) {
		var reader = new FileReader();
		reader.onload = function(e) {
			var content = e.target.result;
			var seriesData = parseContent(content);
			var defaultSeriesName = file.name;
	
			/* todo: check for duplicates and invalid data */
			var newSeries = {
				id: defaultSeriesName,
				name: defaultSeriesName,
				data: seriesData,
				type: plotFlags.type,
				marker: {
					enabled: plotFlags.markerEnabled
				}
			};
			chart.addSeries(newSeries);
	
			$('#series-list').append($('<option selected>')
				.append(defaultSeriesName)
				.attr("name", defaultSeriesName));
			$('#series-list').change();
		}
		reader.readAsText(file);
	}
	
	/*********************************************
		functions for series sidebar follow
	*********************************************/
	
	/* display operations on multiple series */
	function seriesListOps() {
		$('#series-list').click(function(e) {
			if (e.target == this) {
				$('#series-list option').removeProp("selected");
				$('#series-list').change();
			}
		});
	
		$('#series-list').change(function() {
			seriesSelected();
		});
	
		$('#add-series').change(function() {
			$('#series-list option').removeProp("selected");
	
			var fileList = ($('#add-series'))[0].files;
			for (var i = 0; i < fileList.length; i++) {
				addSeriesFromFile(fileList[i]);
			}
			$('#add-series').val('');
		});
	
		$('#remove-series').click(function() {
			var selectedOptions = $('#series-list').val();
			$('#series-list option:selected').remove();
	
			$.each(selectedOptions, function(_, seriesName) {
				chart.get(seriesName).remove();

				// reflect in spreadsheet if necessary
				if ($('#sheet-title').text() === seriesName) {
					$('#sheet-title').text("No series selected");
					$('#sheet-data tr').empty();
					console.log($('#sheet-data'));
				}
			});
	
			$('#set-series').invisible();
		});
	
		$('#show-all').click(function() {
			var selectedOptions = $('#series-list').val();
			$.each(selectedOptions, function(_, seriesName) {
				chart.get(seriesName).show();
			});
		});
	
		$('#hide-all').click(function() {
			var selectedOptions = $('#series-list').val();
			$.each(selectedOptions, function(_, seriesName) {
				chart.get(seriesName).hide();
			});
		});
	}
	
	/* on series select */
	function seriesSelected() {
		var selectedOptions = $('#series-list').val();
		$('#set-series').visible();
	
		if (!selectedOptions) {
			$('#set-series').invisible();
		} else if (selectedOptions.length === 1) {
			$('#set-series .one-series').show();
			$('#series-name').show();
			$('#series-data').show();
			$('#series-data').val('');
	
			var seriesName = selectedOptions[0];
			var series = chart.get(seriesName);
			$('#series-name').val(seriesName);
			$('#series-color').val(series.color);
			$('#series-color').spectrum({
				color: series.color,
				showInput: true,
				preferredFormat: 'hex'
			});
			
			$('#series-symbol').val(series.symbol);
		} else {
			$('#set-series .one-series').invisible();
			$('#series-name').invisible();
			$('#series-data').invisible();
		}
	}
	
	/* options for editing currently selected series */
	function editSeriesOptions() {
		$('#series-data').change(function(e) {
			changeSeriesFromFile();
		});
	
		$('#series-name').change(function() {
			var selectedSeries = $('#series-list').val();
			if (selectedSeries.length > 1) {
				alert("Multiple series selected!");
			}
			var curSeries = chart.get(selectedSeries[0]);
			var newName = $('#series-name').val();
	
			if (chart.get(newName)) {
				alert("Series with this name already exists.");
				return;
			}
			renameSeries(curSeries, newName);
		});
	
		$('#series-color').change(function() {
			var selectedSeries = $('#series-list').val();
			$.each(selectedSeries, function(_, seriesName) {
				var curSeries = chart.get(seriesName);
				curSeries.update({
					color: $('#series-color').val()
				});
			});
		});
	
		$('#series-symbol').change(function() {
			var selectedSeries = $('#series-list').val();
			var selectedSymbol = $('#series-symbol').val();
	
			$.each(selectedSeries, function(_, seriesName) {
				var curSeries = chart.get(seriesName);
				curSeries.update({
					marker: {
						symbol: selectedSymbol
					}
				});
			});
		});
	}
	
	function initSeriesList() {
		editSeriesOptions();
		seriesListOps();
	}
	
	function plotMean() {
		var selectedSeries = $('#series-list').val();
		var firstSeries = chart.get(selectedSeries[0]);
		var newSeriesData = new Array();
		$.each(firstSeries.data, function(index, val) {
			newSeriesData[index] = new Array(0, 0);
			newSeriesData[index][0] = val.x;
		});
	
		$.each(selectedSeries, function(_, seriesName) {
			var curSeries = chart.get(seriesName);
			$.each(curSeries.data, function(index, val) {
				newSeriesData[index][1] += val.y;
			});
		});
		$.each(newSeriesData, function(index, _) {
			newSeriesData[index][1] /= selectedSeries.length;
		});
	
		var defaultSeriesName = "Average " + chart.series.length;
	
		var newSeries = {
			id: defaultSeriesName,
			name: defaultSeriesName,
			data: newSeriesData,
			type: plotFlags.type,
			marker: {
				enabled: plotFlags.markerEnabled
			}
		};
		chart.addSeries(newSeries);
	
		$('#series-list option').removeAttr("selected");
		$('#series-list').append($('<option selected>')
			.append(defaultSeriesName)
			.attr("name", defaultSeriesName));
		$('#series-list').change();
	}

	/********************
		switching modes
	********************/
	function getSelectedSeries() {
		var seriesList = new Array();
		var selectedOptions = $('#series-list').val();
		$.each(selectedOptions, function(_, seriesName) {
			seriesList.push(chart.get(seriesName));
		});
		return seriesList;
	}

	function otherPlots() {
		$('#gen-mean').click(function() {
			plotMean();
		});

		$('#gen-hist').click(function() {
			var w = window.open('histogram.html', '_blank', 'width=1000, height=600');
			w.origSeries = getSelectedSeries();
		});
	}

	/*********************
	 * series data table *
	 ********************/
	function changeSpreadsheetSeries(seriesName) {
		$('#sheet-title').text(seriesName);

		if ($('#sheet-x-label').length === 0) {
			$('#sheet-header').append($('<tr>')
				.append($('<th>').append(chart.options.xAxis[0].title.text).attr("id", "sheet-x-label"))
				.append($('<th>').append(chart.options.yAxis[0].title.text).attr("id", "sheet-y-label")));
		}

		var series = chart.get(seriesName);
		$('#sheet-data').empty();
		$.each(series.data, function(_, pt) {
			$('#sheet-data').append($('<tr>')
				.append($('<td>').append(pt.x))
				.append($('<td>').append(pt.y)));
		});
	}

	function initSpreadsheet() {
		$('#sheet-series-x').change(function() {
			var x = parseFloat($('#sheet-series-x').val());
			var found = false;

			if ($('#sheet-data td').length > 0) {
				var series = chart.get($('#sheet-title').text());
				for (var i = 0; i < series.data.length; i++) {
					if (x === series.data[i].x) {
						var row = $('#sheet-data tr')[i];
						$('#spreadsheet-panel').scrollTop(0);
						$('#spreadsheet-panel').animate({
							scrollTop: $(row).offset().top
						}, 100);
						found = true;
						break;
					}
				}
			}

			if (found) {
				$('.sheet-search-error').css('visibility', 'hidden');
			} else {
				$('.sheet-search-error').css('visibility', 'visible');
			}
		});
	}

})();
