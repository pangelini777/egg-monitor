"use client";

import { useRef, useEffect } from 'react';
import * as d3 from 'd3';

const EggChart = ({ data, width = 400, height = 200, timeRange = 60 }) => {
  const svgRef = useRef(null);

  useEffect(() => {
    if (!data || data.length === 0) return;

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
    const now = Date.now() / 1000; // Current time in seconds
    const xScale = d3.scaleLinear()
      .domain([now - timeRange, now])
      .range([0, innerWidth]);

    const yScale = d3.scaleLinear()
      .domain([-1, 1]) // EGG data typically ranges from -1 to 1
      .range([innerHeight, 0]);

    // Create line generator
    const line = d3.line()
      .x(d => xScale(d.timestamp))
      .y(d => yScale(d.value))
      .curve(d3.curveMonotoneX);

    // Filter data to only show points within the time range
    const filteredData = data.filter(d => d.timestamp >= now - timeRange);

    // Add the line path
    svg.append("path")
      .datum(filteredData)
      .attr("fill", "none")
      .attr("stroke", "#0ea5e9") // Tailwind primary-500
      .attr("stroke-width", 2)
      .attr("d", line);

    // Add data points
    svg.selectAll(".data-point")
      .data(filteredData)
      .enter()
      .append("circle")
      .attr("class", "data-point")
      .attr("cx", d => xScale(d.timestamp))
      .attr("cy", d => yScale(d.value))
      .attr("r", 3)
      .attr("fill", "#0ea5e9");

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
