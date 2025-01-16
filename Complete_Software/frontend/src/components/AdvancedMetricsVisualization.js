import React, { useRef, useEffect, useState } from 'react';
import * as d3 from 'd3';
import { useTheme } from '@mui/material/styles';
import { motion, AnimatePresence } from 'framer-motion';

const AdvancedMetricsVisualization = ({ data, type = 'timeline' }) => {
    const svgRef = useRef(null);
    const theme = useTheme();
    const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
    const [hoveredData, setHoveredData] = useState(null);

    useEffect(() => {
        const updateDimensions = () => {
            if (svgRef.current) {
                const { width, height } = svgRef.current.getBoundingClientRect();
                setDimensions({ width, height });
            }
        };

        updateDimensions();
        window.addEventListener('resize', updateDimensions);
        return () => window.removeEventListener('resize', updateDimensions);
    }, []);

    useEffect(() => {
        if (!data || !dimensions.width) return;

        const svg = d3.select(svgRef.current);
        svg.selectAll('*').remove();

        switch (type) {
            case 'timeline':
                renderTimelineChart(svg, data, dimensions);
                break;
            case 'correlation':
                renderCorrelationMatrix(svg, data, dimensions);
                break;
            case 'heatmap':
                renderHeatmap(svg, data, dimensions);
                break;
            default:
                renderTimelineChart(svg, data, dimensions);
        }
    }, [data, dimensions, type, theme]);

    const renderTimelineChart = (svg, data, dimensions) => {
        const margin = { top: 20, right: 30, bottom: 30, left: 60 };
        const width = dimensions.width - margin.left - margin.right;
        const height = dimensions.height - margin.top - margin.bottom;

        const x = d3.scaleTime()
            .domain(d3.extent(data, d => d.timestamp))
            .range([0, width]);

        const y = d3.scaleLinear()
            .domain([0, d3.max(data, d => d.value)])
            .range([height, 0]);

        const line = d3.line()
            .x(d => x(d.timestamp))
            .y(d => y(d.value))
            .curve(d3.curveMonotoneX);

        const g = svg.append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);

        // Add axes
        g.append('g')
            .attr('transform', `translate(0,${height})`)
            .call(d3.axisBottom(x));

        g.append('g')
            .call(d3.axisLeft(y));

        // Add line
        g.append('path')
            .datum(data)
            .attr('fill', 'none')
            .attr('stroke', theme.palette.primary.main)
            .attr('stroke-width', 2)
            .attr('d', line);

        // Add interactive elements
        const tooltip = d3.select('body').append('div')
            .attr('class', 'tooltip')
            .style('opacity', 0);

        g.selectAll('circle')
            .data(data)
            .enter()
            .append('circle')
            .attr('cx', d => x(d.timestamp))
            .attr('cy', d => y(d.value))
            .attr('r', 4)
            .attr('fill', theme.palette.primary.main)
            .on('mouseover', (event, d) => {
                setHoveredData(d);
                tooltip.transition()
                    .duration(200)
                    .style('opacity', .9);
                tooltip.html(`Value: ${d.value}<br/>Time: ${d.timestamp}`)
                    .style('left', (event.pageX + 10) + 'px')
                    .style('top', (event.pageY - 28) + 'px');
            })
            .on('mouseout', () => {
                setHoveredData(null);
                tooltip.transition()
                    .duration(500)
                    .style('opacity', 0);
            });
    };

    return (
        <div className="advanced-visualization">
            <svg ref={svgRef} width="100%" height="400">
                <defs>
                    <clipPath id="chart-area">
                        <rect x="0" y="0" width="100%" height="100%" />
                    </clipPath>
                </defs>
            </svg>
            <AnimatePresence>
                {hoveredData && (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0 }}
                        className="tooltip-card"
                    >
                        <h4>Metric Details</h4>
                        <p>Value: {hoveredData.value}</p>
                        <p>Time: {hoveredData.timestamp.toLocaleString()}</p>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default AdvancedMetricsVisualization; 