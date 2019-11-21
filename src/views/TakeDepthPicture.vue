<template>
    <v-container>
        <v-layout wrap>
            <v-flex xs12 style="margin-bottom:15px">
                <v-text-field label="Bot IP" v-model="botIp" />
                <v-btn @click="takeDepthPicture()">Take Depth Picture</v-btn>
                <div>Max Value: {{maxValue}}</div>
                <div>Min Value: {{minValue}}</div>
                Paste depth data here and click submit to render it
                <v-textarea v-model="textareaData" cols="50" rows="300"></v-textarea>
                <v-btn @click="renderTextareaData()">Submit</v-btn>
            </v-flex>
            <v-flex xs12 >
                <div id="my_dataviz"></div>
            </v-flex>
        </v-layout>
        
    </v-container>
</template>

<script>
import * as d3 from 'd3';

export default {
    data() {
        return {
            botIp: "10.10.0.7",
            maxValue: 0,
            minValue: 0,
            DEPTH_IMAGE_WIDTH: 320,
            DEPTH_IMAGE_HEIGHT: 240,
            GRAPH_SCALE: 3,
            textareaData: ""
        }
    },
    methods: {
        takeDepthPicture() {
            Promise.race([
                fetch(`http://${this.botIp}/api/cameras/depth`, {
                    method: 'GET'
                }),
                new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 10000))
            ])
            .then(response => response.json())
            .then(jsonData => {
                console.log('depth picture json data:');
                console.log(jsonData);
                this.parseAndRenderData(jsonData.result.image);
            })
            .catch(err => {
                console.log(err);
            })
        },
        renderTextareaData() {
            this.renderGraph(JSON.parse(this.textAreaData));
        },
        parseAndRenderData(rawData) {
            this.renderGraph(this.parseRawData(rawData));
        },
        parseRawData(rawData) {
            var data = [];
            var rawDataIndex = 0;
            let max = 0;
            let min = Infinity;
            // The data from the depth sensor appears to be
            // indexed from the top right
            for (var y=0; y<this.DEPTH_IMAGE_HEIGHT; y++) {
                for (var x=0; x<this.DEPTH_IMAGE_WIDTH; x++) {
                    var value = rawData[rawDataIndex] == "NaN" ? 0 : rawData[rawDataIndex];
                    // convert 'NaN' values which are too
                    // far (or close?) for the sensor to detect. Don't invert
                    // 0 values so they show up as black on the screen
                    if (value != 0) {
                        // invert the colors so things that are closer
                        // show up brighter
                        value = 10000 - value;
                    }
                    data.unshift({ x, y, value });
                    rawDataIndex++;
                    if(value > max) {
                        max = value;
                    }
                    if(value < min) {
                        min = value;
                    }
                }
            }
            console.log(data)
            this.maxValue = max;
            this.minValue = min;
            return data
        },
        renderGraph (data) {
            // d3.js heatmap https://www.d3-graph-gallery.com/graph/heatmap_basic.html
            const margin = {top: 20, right: 30, bottom: 30, left: 30},
                width = this.DEPTH_IMAGE_WIDTH * this.GRAPH_SCALE - margin.left - margin.right,
                height = this.DEPTH_IMAGE_HEIGHT * this.GRAPH_SCALE - margin.top - margin.bottom;

            // append the svg object to the body of the page
            var svg = d3.select("#my_dataviz")
                .append("svg")
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
                .append("g")
                .attr("transform",
                        "translate(" + margin.left + "," + margin.top + ")");

            var xDomain = d3.map(data, function(d){return d.x;}).keys()
            var yDomain = d3.map(data, function(d){return d.y;}).keys()

            // Build X scales and axis:
            var x = d3.scaleBand()
                .range([ width, 0 ])
                .domain(xDomain)
                .padding(0.05);

            // Build Y scales and axis:
            var y = d3.scaleBand()
                .range([ height, 0 ])
                .domain(yDomain)
                .padding(0.05);

            // Build color scale
            var myColor = d3.scaleSequential()
                .interpolator(d3.interpolateInferno)
                .domain([0,10000])

            // create a tooltip
            var tooltip = d3.select("#my_dataviz")
                .append("div")
                .style("opacity", 0)
                .attr("class", "tooltip")
                .style("background-color", "white")
                .style("border", "solid")
                .style("border-width", "2px")
                .style("border-radius", "5px")
                .style("padding", "5px")

            // Three function that change the tooltip when user hover / move / leave a cell
            var mouseover = function(d) {
                tooltip.style("opacity", 1)
            }
            var mousemove = function(d) {
                tooltip
                .html("The exact value of<br>this cell is: " + d.value)
                .style("left", (d3.mouse(this)[0]+70) + "px")
                .style("top", (d3.mouse(this)[1]) + "px")
            }
            var mouseleave = function(d) {
                tooltip.style("opacity", 0)
            }
            // add the squares
            svg.selectAll()
                .data(data, function(d) {return d.x+':'+d.y;})
                .enter()
                .append("rect")
                .attr("x", function(d) { return x(d.x) })
                .attr("y", function(d) { return y(d.y) })
                .attr("rx", 4)
                .attr("ry", 4)
                .attr("width", x.bandwidth() )
                .attr("height", y.bandwidth() )
                .style("fill", function(d) { return myColor(d.value)} )
                .style("stroke-width", 4)
                .style("stroke", "none")
                .style("opacity", 0.8)
                .on("mouseover", mouseover)
                .on("mousemove", mousemove)
                .on("mouseleave", mouseleave)

            // Add title to graph
            svg.append("text")
                .attr("x", 0)
                .attr("y", -50)
                .attr("text-anchor", "left")
                .style("font-size", "22px")
                .text("Misty depth image");

            // Add subtitle to graph
            svg.append("text")
                .attr("x", 0)
                .attr("y", -20)
                .attr("text-anchor", "left")
                .style("font-size", "14px")
                .style("fill", "grey")
                .style("max-width", 400)
                .text("This graph is a representation of what misty's occipital core sees");
        },
    },

}
</script>