"use client";

import { useRef, useEffect } from 'react';
import * as d3 from 'd3';

const EggChart = ({ data, width = 400, height = 200, timeRange = 60, fixedYDomain = null }) => {
  const svgRef = useRef(null);

  useEffect(() => {
    if (!data || data.length === 0) {
      return;
    }
    

    // Clear any existing chart
    d3.select(svgRef.current).selectAll("*").remove();

    // Set up dimensions
    const margin = { top: 20, right: 20, bottom: 30, left: 40 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    // Create SVG
    const svg = d3.select(svgRef.current)
      .attr("width", width)
      .attr("height", height)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Set up scales
    // Get the current time in seconds
    const now = Date.now() / 1000; // Current time in seconds
    
    // Use the current time and timeRange to determine the x-axis scale
    // This ensures we're showing data within the specified time range
    const minTime = now - timeRange;
    const maxTime = now;
    

    
    if (data.length > 0) {
      // Extract timestamps for debugging
      const timestamps = data.map(d => typeof d.timestamp === 'number' ? d.timestamp : parseFloat(d.timestamp));

      
      // Log min and max timestamps in the data
      const dataMinTime = Math.min(...timestamps);
      const dataMaxTime = Math.max(...timestamps);

    }
    
    const xScale = d3.scaleLinear()
      .domain([minTime, maxTime])
      .range([0, innerWidth]);

    // Calculate y domain based on data or use fixed domain
    const calculateYDomain = (data, padding = 0.1) => {
      if (!data || data.length === 0) return [-1, 1]; // Default domain
      
      // Find min and max values
      const minValue = Math.min(...data.map(d => d.value));
      const maxValue = Math.max(...data.map(d => d.value));
      
      // Calculate range
      const range = maxValue - minValue;
      
      // Add padding
      const paddingAmount = range * padding;
      
      // Return domain with padding, but ensure it's at least -1 to 1
      return [
        Math.max(-1, minValue - paddingAmount),
        Math.min(1, maxValue + paddingAmount)
      ];
    };

    // Filter data to only show points within the time range
    // First convert all timestamps to numbers for consistent comparison
    const processedData = data.map(d => ({
      timestamp: typeof d.timestamp === 'number' ? d.timestamp : parseFloat(d.timestamp),
      value: typeof d.value === 'number' ? d.value : parseFloat(d.value)
    })).filter(d => !isNaN(d.timestamp) && !isNaN(d.value));
    
    // Sort data by timestamp (ascending)
    const sortedData = [...processedData].sort((a, b) => a.timestamp - b.timestamp);
    
    // Filter to only include data points from the last 'timeRange' seconds
    const filteredData = sortedData.filter(d => d.timestamp >= minTime && d.timestamp <= maxTime);
    

    const yDomain = fixedYDomain || calculateYDomain(filteredData);
    const yScale = d3.scaleLinear()
      .domain(yDomain)
      .range([innerHeight, 0]);

    // Create line generator with defined check to handle missing or invalid values
    const line = d3.line()
      .defined(d => {
        // Check if both timestamp and value are valid numbers
        const timestamp = typeof d.timestamp === 'number' ? d.timestamp : parseFloat(d.timestamp);
        const value = typeof d.value === 'number' ? d.value : parseFloat(d.value);
        return !isNaN(timestamp) && !isNaN(value);
      })
      .x(d => {
        // Ensure timestamp is a number
        const timestamp = typeof d.timestamp === 'number' ? d.timestamp : parseFloat(d.timestamp);
        return xScale(timestamp);
      })
      .y(d => {
        // Ensure value is a number
        const value = typeof d.value === 'number' ? d.value : parseFloat(d.value);
        return yScale(value);
      })
      .curve(d3.curveCardinal.tension(0.5));

    // Add background
    svg.append("rect")
      .attr("x", 0)
      .attr("y", 0)
      .attr("width", innerWidth)
      .attr("height", innerHeight)
      .attr("fill", "#f8fafc") // Tailwind slate-50
      .attr("rx", 4);
      
    // Add a baseline at y=0
    svg.append("line")
      .attr("x1", 0)
      .attr("y1", yScale(0))
      .attr("x2", innerWidth)
      .attr("y2", yScale(0))
      .attr("stroke", "#e5e7eb")
      .attr("stroke-width", 1)
      .attr("stroke-dasharray", "4,4");
      
    // Add the line path
    if (filteredData.length > 0) {
      try {
        // Data is already sorted by timestamp from the filtering step
        const chartData = filteredData;
        

        
        const pathData = line(chartData);
        
        // Draw the line
        svg.append("path")
          .datum(chartData)
          .attr("fill", "none")
          .attr("stroke", "#10b981") // Tailwind green-500
          .attr("stroke-width", 2)
          .attr("d", line);
        
        // Add data points as circles for visibility
        svg.selectAll("circle")
          .data(chartData)
          .enter()
          .append("circle")
          .attr("cx", d => {
            const timestamp = typeof d.timestamp === 'number' ? d.timestamp : parseFloat(d.timestamp);
            return xScale(timestamp);
          })
          .attr("cy", d => {
            const value = typeof d.value === 'number' ? d.value : parseFloat(d.value);
            return yScale(value);
          })
          .attr("r", 3)
          .attr("fill", "#10b981")
          .attr("stroke", "white")
          .attr("stroke-width", 1);
          
        // Highlight the latest data point with a larger, red circle
        if (chartData.length > 0) {
          const latest = chartData[chartData.length - 1];
          svg.append("circle")
            .attr("cx", xScale(typeof latest.timestamp === 'number' ? latest.timestamp : parseFloat(latest.timestamp)))
            .attr("cy", yScale(typeof latest.value === 'number' ? latest.value : parseFloat(latest.value)))
            .attr("r", 6)
            .attr("fill", "red")
            .attr("stroke", "white")
            .attr("stroke-width", 2);
        }
      } catch (error) {
        console.error('Error generating line path:', error);
      }
    } 

    // Add grid lines
    svg.append("g")
      .attr("class", "grid")
      .attr("transform", `translate(0,${innerHeight})`)
      .call(d3.axisBottom(xScale)
        .ticks(5)
        .tickSize(-innerHeight)
        .tickFormat("")
      )
      .call(g => g.select(".domain").remove())
      .call(g => g.selectAll(".tick line")
        .attr("stroke", "#e5e7eb")
        .attr("stroke-opacity", 0.7)
      );

    svg.append("g")
      .attr("class", "grid")
      .call(d3.axisLeft(yScale)
        .ticks(5)
        .tickSize(-innerWidth)
        .tickFormat("")
      )
      .call(g => g.select(".domain").remove())
      .call(g => g.selectAll(".tick line")
        .attr("stroke", "#e5e7eb")
        .attr("stroke-opacity", 0.7)
      );

    // Add axes
    const xAxis = d3.axisBottom(xScale)
      .ticks(5)
      .tickFormat(d => `${Math.round(now - d)}s`);

    const yAxis = d3.axisLeft(yScale)
      .ticks(5);

    svg.append("g")
      .attr("transform", `translate(0,${innerHeight})`)
      .call(xAxis);

    svg.append("g")
      .call(yAxis);

    // Add axis labels
    svg.append("text")
      .attr("text-anchor", "middle")
      .attr("x", innerWidth / 2)
      .attr("y", innerHeight + margin.bottom - 5)
      .attr("fill", "currentColor")
      .attr("font-size", "10px")
      .text("Time (seconds ago)");

    svg.append("text")
      .attr("text-anchor", "middle")
      .attr("transform", "rotate(-90)")
      .attr("y", -margin.left + 10)
      .attr("x", -innerHeight / 2)
      .attr("fill", "currentColor")
      .attr("font-size", "10px")
      .text("EGG Value");

  }, [data, width, height, timeRange]);

  return (
    <div className="bg-white p-2 rounded-md">
      {data && data.length > 0 ? (
        <svg ref={svgRef} width={width} height={height}></svg>
      ) : (
        <div 
          className="flex items-center justify-center"
          style={{ width, height }}
        >
          <p className="text-gray-500">No data available</p>
        </div>
      )}
    </div>
  );
};

export default EggChart;
