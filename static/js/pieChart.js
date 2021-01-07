
var w = 600
var h = 400
var p = 100
var bar_w = 50
var bar_p = 15

// console.log(boardName)

svg();
bind(data);
render();

//繪圖區
function svg() {
    d3.select("#barChart")
        .append("svg")
        .attr({
            width: w,
            height: h,
        })
}

//綁定資料
function bind(data) {
    //rect
    var selection = d3.select("#barChart>svg")
        .selectAll("rect")
        .data(data);

    selection.enter().append("rect");
    selection.exit().remove();


    //text
    var selection_text = d3.select("#barChart>svg")
        .selectAll("text")
        .data(data);

    selection_text.enter().append("text");
    selection_text.exit().remove();
}

//渲染
function render() {
    //rect
    d3.selectAll("rect")
        .attr({
            x: (d, i) => {
                return p + bar_p + (bar_w + bar_p) * i;
            },
            y: (d, i) => {
                return h - p - d;
            },
            width: bar_w,
            height: (d) => {
                return d
            },
            fill: (d)=>{
                if (d>100){
                    return "lightgreen";
                }
                else{
                    return "red";
                }
            },
            "id": (d, i)=>{
                return boardName[i];
            }
        })
      

    //text
    d3.selectAll("text")
        .attr({
            x: (d, i) => {
                return p + bar_p + (bar_w + bar_p) * i + bar_w / 2 - 8;
            },
            y: (d, i) => {
                return h - p - d - 5;
            },
            "font-size": 15
        })
        .text((d) => {
            return d
        })

    // axis
    var xScale = d3.scale.linear()
        .domain([0, data.length-1])
        .rangeRound([0, w-2*p])

    var yScale = d3.scale.linear()
        .domain([d3.min(data), d3.max(data)])
        .range([h-p, 0])

    var xAxis = d3.svg.axis()
        .scale(xScale)
        .orient("bottom")
        .ticks(7)
        .tickFormat((d)=>{
            return boardName[d];
        })
    
    var yAxis = d3.svg.axis()
        .scale(yScale)
        .orient("left")
        .ticks(7)
        .tickFormat((d)=>{
            return d+"個";
        })

    d3.select("#barChart>svg")
        .append("g")
        .classed("axis", true)
        .attr("transform", "translate("+(p)+"," + (h - p) + ")")
        .call(xAxis);

    d3.select("#barChart>svg")
        .append("g")
        .classed("axis", true)
        .attr("transform", "translate("+(p)+", 0)")
        .call(yAxis);

    // bind(boardName)
    // d3.select("#barChart>svg")
    //     .append("text")
    //     .attr({
    //         // "text-anchor": "middle",
    //         "font-size": 15,
    //         x: (d, i)=>{
    //             return p + bar_p + (bar_w + bar_p) * i + bar_w / 2 - 8;
    //         },
    //         y: (d, i)=>{
    //             return h - p - data[i] - 5;
    //         }
    //     })
    //     .text((d)=>{
    //         return d;
    //     })
    
}



