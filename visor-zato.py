#!/usr/bin/env python
# -*- coding: utf-8 -*-
from zato.server.service import Service


class CovidMakers(Service):

    def handle(self):
        self.response.content_type = 'text/html; charset=utf-8'
        self.response.payload = """


<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"
        integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
    <script src="https://code.jquery.com/jquery-3.3.1.min.js"
        integrity="sha256-FgpCb/KJQlLNfOu91ta32o/NMZxltwRo8QtmkMRdAu8=" crossorigin="anonymous">
        </script>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.3.1/dist/leaflet.css"
        crossorigin="" />
    <script src="https://unpkg.com/leaflet@1.3.1/dist/leaflet.js"
        crossorigin=""></script>
    <link href="https://stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css" rel="stylesheet">
    <script
        src='https://api.tiles.mapbox.com/mapbox.js/plugins/leaflet-omnivore/v0.3.1/leaflet-omnivore.min.js'></script>
    <script type="text/javascript" src="http://158.49.112.127:11223/zlibjs"></script>
    <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/@turf/turf@5/turf.min.js"></script>
    <script src="//cdnjs.cloudflare.com/ajax/libs/socket.io/2.2.0/socket.io.js" integrity="sha256-yr4fRk/GU1ehYJPAs8P4JlTgu0Hdsp4ZKrx8bDEDC3I=" crossorigin="anonymous"></script>

    <script src="http://158.49.112.127:11223/sidebar_leaflet_js"></script>
    <link rel="stylesheet" href="http://158.49.112.127:11223/sidebar_leaflet_css" />
    <script src="https://cdn.jsdelivr.net/npm/json-formatter-js@2.3.4/dist/json-formatter.umd.min.js"></script>

    <style>
        #mapid {
            position: absolute;
            width: 100%;
            top: 0;
            /* The height of the header */
            bottom: 0;
            left: 0;
        }

        .margin-left-1rem {
            margin-left: 1rem;
        }

        .padding-left-1rem {
            padding-left: 1rem;
        }

        .padding-left-3rem {
            padding-left: 3rem;
        }
    </style>
    <title>Map Box Testing</title>
</head>

<body>
    <div id='mapid'></div>

    <div id="sidebar" class="sidebar  sidebar-rigth collapsed">
        <div class="sidebar-tabs">
            <ul role="tablist">
            <li><a href="#makers" role="tab">  <i class="fa fa-caret-left"></i></a></li>
            <li><a href="#demands" role="tab">  <i class="fa fa-caret-left"></i></a></li>

            </ul>
        </div>
        <div   class="sidebar-content">
            <div class="sidebar-pane"  id="makers">
                <h1 class="sidebar-header">
                    Makers
                    <span class="sidebar-close"><i class="fa fa-caret-right"></i></span>
                </h1>
                <div id="makers_html">
                    
                </div>
            </div>

            <div class="sidebar-pane"  id="demands">
                <h1 class="sidebar-header">
                    Demanda
                    <span class="sidebar-close"><i class="fa fa-caret-right"></i></span>
                </h1>
                <div id="demands_html">
                    
                </div>
            </div>
        </div>
    </div>

    
    <script>
        //Create the map object and insert the div with id 'mapid'. The initial coordinates 39.47.. and -6.34.. are selected. 
        // and zoom 20.
        var map = L.map('mapid', { zoomDelta: 0.5, zoomSnap: 0.5, zoomControl: false}).setView([39.47649, -6.37224], 20);

        //Loading the map display layer.
        var streets = L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/streets-v10/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoiZmFoYW5pIiwiYSI6ImNqMTZiYm4xMjAyYjEzMnFxdmxnd2V3cHkifQ.-8Hau4tMxMiiSF-9D5AAYA', { maxZoom: 25 }).addTo(map);
        var sidebar =  L.control.sidebar('sidebar',  { position: 'right'} ).addTo(map);

        
        //Action executed at the end of a movement on the display.
        map.on('moveend', function onDragEnd(s) {
            //console.log(map.getZoom());
            processNodes(makers, 'makers');
            processNodes(demand, 'demands');
        });

        var makers = [];
        var demand = [];

        var layers = [];
        var layersIds = {};
        
        
        defineDiff();
        // Crea una nueva conexión.
        //const socket = new WebSocket('ws://localhost:8080');
        var socket = io('ws://158.49.112.158:8443');
        
        socket.emit('connect', {data: 'Caceres'});
        
        setInterval(function(){ socket.emit('ping', {data : ""}); }, 900);

        socket.on('connection_response', function (msg) {
            console.log('Message from server', msg.data);
            res = msg.data;
            if (res) {
                var keys = Object.keys(res.demand);
                names = demand.map((m) =>  m.usuario);

                keys.forEach(function(key){
                    if (!names.find(ele => key == ele)) {
                        demand.push(res.demand[key]);
                    }
                });

                var keys = Object.keys(res.makers);
                names = makers.map((m) =>  m.usuario);

                keys.forEach(function(key){
                    if (!names.find(ele => key == ele)) {
                        makers.push(res.makers[key]);
                    }
                });

                var formatter = new JSONFormatter(makers);
                $("#makers_html").html(formatter.render())
                formatter.openAtDepth(5);

                var formatter = new JSONFormatter(demand);
                $("#demands_html").html(formatter.render())
                formatter.openAtDepth(5);
                //res.demand.push(...res.makers);
                processNodes(makers, 'makers');
                processNodes(demand, 'demands');
            }
        });

        socket.on('update', function (msg) {
            console.log('Update from server', msg);
            res = msg.data;

           

            d_names = demand.map((m) =>  m.usuario);
            m_names = makers.map((m) =>  m.usuario);

            console.log(res);
            if (res) {
                for (i = 0; i < res.length; i++) {
                    if (res[i][0] == 'change') {
                        if (res[i][1][0] == "makers") {
                            var n = makers.filter((n) => n.usuario == res[i][1][1])[0];
                            var attrs = res[i][1][2];
                            var values = res[i][2][1];
                            n[attrs] = values;
                        } else if (res[i][1][0] == 'demands') {
                            var n = demand.filter((n) => n.usuario == res[i][1][1])[0];
                            var attrs = res[i][1][2];
                            var values = res[i][2][1];
                            n[attrs] = values;
                        }
                    } else if (res[i][0] == 'add') {
                        if (res[i][1][0] == "makers") {
                            if (!m_names.find(ele => ele == res[i][2][0][1].usuario)) {
                                makers.push(res[i][2][0][1]);
                            }
                        } else if  (res[i][1][0] == "demands") {  
                            if (!d_names.find(ele => ele == res[i][2][0][1].usuario)) {
                                demand.push(res[i][2][0][1]);
                            }
                        }
                    } else if (res[i][0] == 'remove') {
                        if (res[i][1][0] == "makers") {
                            makers = makers.filter((n) => n.usuario != res[i][2][0][1].usuario);
                        } else if  (res[i][1][0] == "demands") {  
                            demand = demand.filter((n) => n.usuario != res[i][2][0][1].usuario);
                            
                        }
                    }
                }

                var formatter = new JSONFormatter(makers);
                $("#makers_html").html(formatter.render())
                formatter.openAtDepth(5);

                var formatter = new JSONFormatter(demand);
                $("#demands_html").html(formatter.render())
                formatter.openAtDepth(5);

                processNodes(makers, 'makers', true);
                processNodes(demand, 'demands', true);
            }
        });



        /*
        //It doesn't work until we put https in zato
        //Put a marker in the user position
        function onLocationFound(e) {
            var radius = e.accuracy;

            L.marker(e.latlng).addTo(map)
                .bindPopup("You are within " + radius + " meters from this point").openPopup();

            L.circle(e.latlng, radius).addTo(map);
        }

        //callback invoked when the location is found.
        map.on('locationfound', onLocationFound);

        //Get the location every 5 seconds
        locate = () => map.locate({setView: true, maxZoom: 16});
        setInterval(locate, 5000);
        */





        function processNodes(nodes, type, removeAll=false) {

            let nodesToDraw = {};
            let matchedNodes = [];
            var nodesToRemove = [];
            //Get the nodes we are going to Draw

          

            matchingNodes(nodes, matchedNodes, nodesToDraw);

            if (!layersIds[type]) {layersIds[type] = [] }
            if (removeAll){  nodesToRemove = layersIds[type].diff([]) }
            else {  nodesToRemove = layersIds[type].diff(matchedNodes) }
            removeNodes(nodesToRemove, type);

            if (Object.keys(nodesToDraw)){
                Object.keys(matchedNodes).forEach(function (nodeToAdd) {
                    node = matchedNodes[nodeToAdd]
                    if (!layers[node]) {

                        //if (isJson(nodesToDraw[node].geojson )) {
                        layersIds[type].push(node);
                        drawNode(layers, nodesToDraw, node, type);
                        //}
                    }
                });
            }

        }

        //The function iterates the list of nodes and selects those to be drawn.  
        //This is done by checking the zoom of the viewer, the selected filters and the selected floor.
        function matchingNodes(nodes, matchedNodes, nodesToDraw) {
            // function generateRandomNumber(min, max) {
            //     return  Math.random() * (max - min) + min;
                
            // };
            nodes.forEach(function (node) {
                //console.log(node, node.lat, node.ling);
                // if (node.lat == "" && node.long == "") {
                //     node.lat = generateRandomNumber(39.464, 39.479);
                //     node.long = generateRandomNumber(-6.371, -6.374);
                // }
                //console.log(node.lat, node.long)
            
                node.lat = parseFloat(node.lat)
                node.long = parseFloat(node.long)
                
                if (isNaN(node.lat) || isNaN(node.long)) { return }

                if (node.lat != "" && node.long != "" && map.getBounds().contains([parseFloat(node.lat), parseFloat(node.long)]))
                    matchedNodes.push(node.usuario);
                    nodesToDraw[node.usuario] = node;
            });
        }


        let  markerHtmlStyles = (color) =>  new String(`
        background-color: ${color};
        width: 3rem;
        height: 3rem;
        display: block;
        left: -1.5rem;
        top: -1.5rem;
        position: relative;
        border-radius: 3rem 3rem 0;
        transform: rotate(45deg);
        border: 1px solid #FFFFFF`);

        let icon =  (color, class_, number) => { 

            return new L.divIcon({
                    className: class_,
                    iconAnchor: [0, 24],
                    labelAnchor: [-6, 0],
                    popupAnchor: [0, -36],
                    //<span style="${Html}" />
                    html: `<label style="
                        background: none repeat scroll 0 0 ${color};
                        display: table;
                        border: 1px solid #ffffff;
                        border-radius: 50%;
                        color: #fff;
                        font-size: 20px;
                        font-weight: bold;
                        padding: 5px 10px;
                        position: relative;
                        min-width: 40px;
                        min-height: 40px;
                        text-align: center;
                   "> ${ String(number != undefined ? number : " ") } </label>`
            }) 
        };


        let geojson = (coord) => `{
        "type": "Point", 
        "coordinates": [${coord}]
        }`;


        //Draw a node on the map
        function drawNode(layers, nodesToDraw, nodeToAdd, type) {
            //var marker = L.marker([node.lat, node.long], node.icon);
            var color = "";
            var popUp = "";

            let n = nodesToDraw[nodeToAdd];
            //nodesToDraw[Object.keys(nodesToDraw)[nodeToAdd]];
            if (type == 'demands') { 
                popUp = `Usuario: ${n.usuario} <br>
                Cantidad necesaria actual : ${n["cantidad necesaria actual"]} <br>
                Entregadas : ${n.entregadas} <br>
                Persona de contacto : ${n["persona de contacto"]}  <br>
                Localidad : ${n.Localidad} <br>`;
                color = icon("#48C713", "demands", n["cantidad necesaria actual"]); 
            }
            if (type == 'makers') { 
                popUp = `Usuario: ${n.usuario} <br>
                Capacidad diaria : ${n[ "capacidad diaria"]} <br>
                Cantidad actual : ${n["cantidad actual"]} <br>
                Entregadas : ${n.entregadas} <br>
                Capacidad diaria : ${n["capacidad diaria"]} <br>
                Localidad : ${n.Localidad}<br>
                Dirección : ${n["direccion"]}<br>`;
            
                color = icon("#FF00FF", "makers", n["cantidad actual"]) ; 
            }
            //console.log(type, color)
            try {
                layers[nodeToAdd] = L.marker([n.lat, n.long],  { icon: color });
                layers[nodeToAdd].bindPopup(popUp);
                //Add node to map.
                layers[nodeToAdd].addTo(map);     
            } catch (error) {
                
            }
           
        }



        //Removen nodes from the map.
        function removeNodes(nodesToRemove, type) {
            nodesToRemove.forEach(function (nodeToRemove) {
                if (layers[nodeToRemove]) {
                    map.removeLayer(layers[nodeToRemove]);
                }
                delete layers[nodeToRemove];

                let index = layersIds[type].indexOf(nodeToRemove);
                if (index > -1) {
                    layersIds[type].splice(index, 1);
                }
            });

        }

        
        //check if object can be parsed to json.
        function isJson(item) {
            item = typeof item !== "string"
                ? JSON.stringify(item)
                : item;

            try {
                item = JSON.parse(item);
            } catch (e) {
                return false;
            }

            if (typeof item === "object" && item !== null) {
                return true;
            }

            return false;
        }

        // Define diff function in arrays
        function defineDiff() {
            Array.prototype.diff = function (a) {
                return this.filter(function (i) {
                    return a.indexOf(i) === -1;
                });
            };
        }

    </script>

</body>

</html>
        """
