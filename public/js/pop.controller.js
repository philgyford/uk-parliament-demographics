;(function() {
  'use strict';
  window.pop = window.pop || {};

  pop.controller = function() {

    var chartSelector = '.pop-chart';

    // Will be the contents of the JSON file.
    var ages;

    // Will be the chart function.
    var chart;

    // Initial chart display.
    var start = {
      'left': 'commonsAll',
      'right': 'lordsAll'
    };

    // Will look like start once we've rendered the chart:
    var current = {};

    // Load the data and render the initial chart.
    d3.json('data/ages.json').then(function(data) {
      processAgesData(data);
      renderChart(start['left'], start['right']);
    });


    /**
     * Put the data from ages.json into a format useful for the interface.
     */
    function processAgesData(data) {
      var options = [
        ['uk', 'UK population'],
        ['commonsAll', 'All MPs'],
        ['lordsAll', 'All Lords'],
      ];

      // Add options to the two select fields.
      ['left', 'right'].forEach(function(side, i) {
        d3.select('.choices-'+side)
            .on('change', onAgesChange)
            .selectAll('option')
              .data(options)
              .enter()
              .append('option')
                .attr('value', function(d) { return d[0]; })
                .property('selected', function(d) { return d[0] === start[side]; })
                .text(function(d) { return d[1]; });
      });

      ages = data;

    };

    /**
     * Looks at current values of the select fields and updates the chart.
     */
    function onAgesChange() {
      // Get which side and what chart to display:
      var select = d3.select(this);
      var clss = select.attr('class');
      var val = d3.select(this).property('value');

      if (clss == 'choices-left') {
        renderChart(val, current['right']);
      } else {
        renderChart(current['left'], val);
      };
    };

    /**
     * Create or update the chart.
     * `left` and `right` are keys used in the object in ages.json.
     * One will be displayed on each side of the chart.
     */
    function renderChart(left, right) {
      var data = [];

      for (var band in ages[left]) {
        // Assuming both left and right have the same bands.
        data.push({
          'band': band,
          'left': ages[left][band],
          'right': ages[right][band],
        })
      };

      if (typeof chart === 'function') {
        // The chart already exists, so update with new data.
        chart.data(data);

      } else {
        // Chart doesn't exist yet, so create it.
        chart = pop.populationPyramidChart().data(data);
        d3.select(chartSelector).call(chart);
      };

      current = {
        'left': left,
        'right': right
      };
    };

  };

}());
