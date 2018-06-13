;(function() {
  'use strict';
  window.parl = window.parl || {};

  parl.populationPyramidChart = function(selection) {
    var margin = {top: 20, right: 20, bottom: 24, left: 20};

    // Space in the middle for the y-axis labels.
    var marginMiddle = 28;

    // Internal things that can't be overridden:
    var xScale = d3.scaleLinear(),
        xScaleL = d3.scaleLinear(),
        xScaleR = d3.scaleLinear(),
        yScale = d3.scaleBand(),
        xAxisL = d3.axisBottom(xScaleL)
                    .tickFormat(d3.format('.0%')),
        xAxisR = d3.axisBottom(xScaleR)
                    .tickFormat(d3.format('.0%')),
        yAxisL = d3.axisRight(yScale)
                    .tickSize(0)
                    .tickPadding(marginMiddle),
        yAxisR = d3.axisLeft(yScale)
                    .tickSize(0)
                    .tickFormat('');

    function chart(selection) {
      selection.each(function(data) {

        var container = d3.select(this),
            svg,
            rowsData = data['rows'];

        // The total counts for each side.
        var totalL = d3.sum(rowsData, function(d) { return d.left; }),
            totalR = d3.sum(rowsData, function(d) { return d.right; }),
            // Functions for getting a value as a percentage of the sides' total.
            percentageL = function(d) { return d / totalL; },
            percentageR = function(d) { return d / totalR; };

        // The highest x value on either side:
        var maxXValue = Math.max(
          d3.max(rowsData, function(d) { return percentageL(d.left); }),
          d3.max(rowsData, function(d) { return percentageR(d.right); })
        );

        // Set up scale domains.
        xScale.domain([0, maxXValue]);
        xScaleL.domain([0, maxXValue]);
        xScaleR.domain([0, maxXValue]);
        yScale.domain(rowsData.map(function(d) { return d.group; }));

        if (!svg) {
          svg = container.append('svg');
          var inner = svg.append('g').classed('chart-inner', true);
        };

        // Groups that will contain the bars on each side.
        var leftGroup = inner.append('g');
        var rightGroup = inner.append('g');

        // Set up axes.
        inner.append("g")
              .classed("axis axis-x axis-left", true);

        inner.append("g")
              .classed("axis axis-x axis-right", true);

        inner.append("g")
              .classed("axis axis-y axis-left", true);

        inner.append("g")
              .classed("axis axis-y axis-right", true);

        // Need to be in a scope available to all the render methods.
        var chartW,
            chartH,
            sideW,
            xLeft0,
            xRight0;

        /**
         * Draws the whole chart. For the first time or on window resize.
         */
        function render() {
          renderScales();
          renderAxes();
          renderBars();
        };

        /**
         * Calculates the scales and sets the size of the chart.
         */
        function renderScales() {
          // Outer width, including space for axes etc:
          var width  = parseInt(container.style('width'), 10),
              height = parseInt(container.style('height'), 10);

          // Inner width, chart area only, minus margins for axes etc.
          chartW = width - margin.left - margin.right;
          chartH = height - margin.top - margin.bottom;

          // The width of each side of the chart:
          sideW = (chartW / 2) - marginMiddle;

          // Where the 0 is on each side's x-axis:
          xLeft0 = sideW;
          xRight0 = chartW - sideW;

          // Set the scales for these dimensions.
          xScale.rangeRound([0, sideW]);
          xScaleL.rangeRound([sideW, 0]);
          xScaleR.rangeRound([0, sideW]);
          yScale.rangeRound([chartH, 0]).padding(0.1);

          // Update outer dimensions.
          svg.transition().attr('width', width)
                          .attr('height', height);

          inner.attr("transform", translation(margin.left, margin.top));
        };

        function renderAxes() {

          // Reverse scale on the left-hand side:
          xAxisL.scale( xScale.copy().range([xLeft0, 0]) );

          xAxisR.scale(xScale);

          svg.select('.axis-x.axis-left')
              .attr('transform', translation(0, chartH))
              .call(xAxisL);

          svg.select('.axis-x.axis-right')
              .attr('transform', translation(xRight0, chartH))
              .call(xAxisR);

          svg.select('.axis-y.axis-left')
              .attr('transform', translation(xLeft0, 0))
              .call(yAxisL)
              .selectAll('text')
              .style('text-anchor', 'middle');

          svg.select('.axis-y.axis-right')
              .attr('transform', translation(xRight0, 0))
              .call(yAxisR);
        };

        function renderBars() {

          // Set positions of the left and right groups, that contain the bars.
          // Left has its scale inverted so the bars go from the centre to left.
          leftGroup.attr('transform', translation(xLeft0, 0) + 'scale(-1,1)');
          rightGroup.attr('transform', translation(xRight0, 0));

          // x, y and height are the same for bars on both sides:
          var barX = 0;
          var barY = function(d) { return yScale(d.group); };
          var barH = yScale.bandwidth();

          // Calculating the width of each bar on left and right:
          var barLW = function(d) { return xScale(percentageL(d.left)); };
          var barRW = function(d) { return xScale(percentageR(d.right)); };

          // Select bars on the left:
          var barsL = leftGroup.selectAll('.chart-bar-left')
                               .data(rowsData);

          barsL.enter()
                .append('rect')
                .attr('class', 'chart-bar chart-bar-left')
                .attr('x', barX)
                .attr('y', barY)
                .attr('width', barLW)
                .attr('height', barH);

          barsL.exit().remove();

          barsL.transition()
                .attr('x', barX)
                .attr('y', barY)
                .attr('width', barLW)
                .attr('height', barH);

          // Now the same for the bars on the right.

          var barsR = rightGroup.selectAll('.chart-bar-right')
                                .data(rowsData)

          barsR.enter()
                .append('rect')
                .attr('class', 'chart-bar chart-bar-right')
                .attr('x', barX)
                .attr('y', barY)
                .attr('width', barRW)
                .attr('height', barH);

          barsR.exit().remove();

          barsR.transition()
                .attr('x', barX)
                .attr('y', barY)
                .attr('width', barRW)
                .attr('height', barH);

        };


        /**
         * Utility function to save manually writing translate().
         */
        function translation(x,y) {
          return 'translate(' + x + ',' + y + ')';
        }

        render();

        window.addEventListener('resize', render);
      });

    };

    chart.margin = function(_) {
      if (!arguments.length) return margin;
      margin = _;
      return chart;
    };

    return chart;
  };

}());
