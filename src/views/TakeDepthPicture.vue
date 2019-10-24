<template>
    <v-container>
        <v-layout wrap>
            <v-flex xs12 style="margin-bottom:15px">
                <v-text-field label="Bot IP" v-model="botIp" />
                <v-btn @click="takeDepthPicture()">Take Depth Picture</v-btn>
                <div>Max Value: {{maxValue}}</div>
                <div>Min Value: {{minValue}}</div>
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
            minValue: 0
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
                this.renderGraph(jsonData.result.image);
            })
            .catch(err => {
                console.log(err);
            })
        },
        renderGraph (rawData) {
            // set the dimensions margins and scale of the graph
            const DEPTH_IMAGE_WIDTH = 320;
            const DEPTH_IMAGE_HEIGHT = 240;
            const GRAPH_SCALE = 3;
            const margin = {top: 20, right: 30, bottom: 30, left: 30},
                width = DEPTH_IMAGE_WIDTH * GRAPH_SCALE - margin.left - margin.right,
                height = DEPTH_IMAGE_HEIGHT * GRAPH_SCALE - margin.top - margin.bottom;

            // append the svg object to the body of the page
            var svg = d3.select("#my_dataviz")
                .append("svg")
                    .attr("width", width + margin.left + margin.right)
                    .attr("height", height + margin.top + margin.bottom)
                .append("g")
                    .attr("transform",
                        "translate(" + margin.left + "," + margin.top + ")");

            // read data
            // var rawData = [];
            // for (var i=0; i<(DEPTH_IMAGE_WIDTH*DEPTH_IMAGE_HEIGHT); i++) {
            //     var value = i % 2000;
            //     rawData.push(value);
            // }
            // console.log(rawData);
            
            var data = [];
            var rawDataIndex = 0;
            let max = 0;
            let min = Infinity;
            for (var y=0; y<DEPTH_IMAGE_HEIGHT; y++) {
                for (var x=DEPTH_IMAGE_WIDTH-1; x>=0; x++) {
                    var value = rawData[rawDataIndex] == "NaN" ? 0 : rawData[rawDataIndex];
                    // 0 values are typically NaN values which are too
                    // far for the sensor to detect. Don't invert
                    // 0 values so they show up as black on the screen
                    if (value != 0) {
                        // invert the colors so things that are closer
                        // show up brighter
                        value = 10000 - value;
                    }
                    data.unshift({ x, y, value: 10000 - value });
                    rawDataIndex++;
                    if(value > max) {
                        max = value;
                    }
                    if(value < min) {
                        min = value;
                    }
                }
            }
            this.maxValue = max;
            this.minValue = min;

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
                .range([ 0, width ])
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