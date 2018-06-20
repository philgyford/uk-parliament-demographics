;(function() {
  'use strict';
  window.pop = window.pop || {};

  pop.controller = function() {

    var chartSelector = '.pop-chart';

    // Will be the contents of the JSON file.
    var ages = {};

    // Will be the chart function.
    var chart;

    // Initial chart display.
    var start = {
      'left': 'commons-all',
      'right': 'lords-all'
    };

    // Will look like start once we've rendered the chart:
    var current = {};

    // Load the data and render the initial chart.
    d3.json('data/chart.json').then(function(data) {
      processAgesData(data);
      renderAgesChart(start['left'], start['right']);
    });


    /**
     * Put the data from chart.json into a format useful for the interface.
     */
    function processAgesData(data) {
      // Will be all the optgroups and their options:
      var optgroups = [
        {
          'name': 'United Kingdom',
          'options': [
            ['uk', 'Adult population']
          ]
        }
      ];

      // Optgroups with empty options:
      var commonsOptgroup = {
        'name': 'House of Commons',
        'options': []
      };
      var lordsOptgroup = {
        'name': 'House of Lords',
        'options': []
      };

      // Populate the optgroups' options:
      data['commons'].forEach(function(d, i) {
        commonsOptgroup['options'].push(
          [ 'commons-'+d['id'], d['name'] ]
        );
      });
      data['lords'].forEach(function(d, i) {
        lordsOptgroup['options'].push(
          [ 'lords-'+d['id'], d['name'] ]
        );
      });

      // Add the two optgroups into the full list:
      optgroups = optgroups.concat(commonsOptgroup);
      optgroups = optgroups.concat(lordsOptgroup);

      // Add options to the two select fields.
      ['left', 'right'].forEach(function(side, i) {
        d3.select('.choices-'+side)
            .on('change', onAgesChange)
          .selectAll('optgroup')
            .data(optgroups)
            .enter()
          .append('optgroup')
            .attr('label', function(d) { return d.name; })
          .selectAll('option')
            .data(function(d) { return d.options; })
            .enter()
          .append('option')
            .attr('value', function(d) { return d[0]; })
            .property('selected', function(d) { return d[0] === start[side]; })
            .text(function(d) { return d[1]; });
      });

      // Put the data into our ages object, for use by the chart.
      for(var key in data) {

        if (key == 'uk') {
          ages[key] = {
            'name': data[key]['name'],
            'ages': data[key]['ages']
          };

        } else {
          data[key].forEach(function(d, i) {
            var nam
            // So it'll be like 'commons-4':
            ages[key + '-' + d['id']] = {
              'name': d['name'],
              'ages': d['ages']
            };
          });
        };

      };

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
        renderAgesChart(val, current['right']);
      } else {
        renderAgesChart(current['left'], val);
      };
    };

    /**
     * Create or update the chart.
     * `left` and `right` are keys used in the object in chart.json.
     * e.g. 'commonsall' or 'uk'.
     * One will be displayed on each side of the chart.
     */
    function renderAgesChart(left, right) {
      var data = [];

      for (var band in ages[left]['ages']) {
        // Assuming both left and right have the same age bands.
        // So each element will be like:
        // {'band': '18-19', 'left': 4, 'right': 12}

        data.push({
          'band': band,
          'left': ages[left]['ages'][band],
          'right': ages[right]['ages'][band],
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


      // Set chart titles.

      var leftTitle = ages[left]['name'];
      var rightTitle = ages[right]['name'];

      if (left.indexOf('commons') === 0) {
        leftTitle = 'House of Commons: ' + leftTitle;
      } else if (left.indexOf('lords') === 0) {
        leftTitle = 'House of Lords: ' + leftTitle;
      };
      if (right.indexOf('commons') === 0) {
        rightTitle = 'House of Commons: ' + rightTitle;
      } else if (right.indexOf('lords') === 0) {
        rightTitle = 'House of Lords: ' + rightTitle;
      };

      d3.select('.title-left').text(leftTitle);
      d3.select('.title-right').text(rightTitle);


      // So we know what's currently showing.
      current = {
        'left': left,
        'right': right
      };
    };

  };

}());
