;(function() {
  'use strict';
  window.pop = window.pop || {};

  pop.controller = function() {

    var chartSelector = '.parl-chart';

    // Will be the contents of the JSON file.
    var ages;

    // Will be the chart function.
    var chart;

    // Load the data and render the initial chart.
    d3.json('data/ages.json').then(function(data) {
      ages = data;
      renderChart('uk', 'mps');
    });


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

    };

  };

}());
