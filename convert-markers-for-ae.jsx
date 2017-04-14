var aFile = File.openDialog ( 'Select text file with timings:', '*.txt', false ) ;
var timings = loadTimings(aFile);

//list of compositions
var compList = app.project.items;

if(compList.length > 0) {

	//1. take the first composition OR
	//var currentComposition = compList[1];
	
	//2. take currently active composition
	var currentComp = app.project.activeItem;

	if(currentComp.layers.length > 0) {

		//take the first layer of the active composition
        var markerLayers = {};
        //var layerCount = 0;
        function getMarkerLayer(trackName) {
            if (!markerLayers[trackName]) {
                //markerLayers[trackName] = currentComp.layer(layerCount + 1);
                var newlayer = currentComp.layers.addNull();
                newlayer.name = trackName;
                markerLayers[trackName]  = newlayer;
                //layerCount++;
                }
            return markerLayers[trackName];
            }

		for (var i = 1; i < timings.length; i++) {
			var parts = timings[i].split('\t');
            var name = parts[0];
            var trackName = parts[1];
            var duration = parseFloat(parts[5]);
            var startTime = parseFloat (parts[3]);
            var endTime = parseFloat(parts[4]);
            var markerVal = new MarkerValue(name);
            
            //var markerLayer = getMarkerLayer(trackName);
            var markerLayer = currentComp.layers.addNull();
            markerLayer.name = name;
            markerLayer.inPoint = startTime;
            markerLayer.outPoint = endTime;
            
            //markerVal.duration = duration;
			//markerLayer.property("Marker").setValueAtTime(startTime, markerVal);
		}	
	}
	else {
		alert("No layer in this composition. Create a layer first. It can be a Null Object layer.");
	}
}
else {
		alert("No composition in the project. Create a composition first. Its duration should be equal or longer than the end timestamp of the last marker.");
	}



//loads markers from Audacity text files with labels
function loadTimings(filePath) {

var timings = new Array ( ) ;

var fileObj = File(filePath);
if ( ! fileObj.exists ) {
return timings ;
}

try {
fileObj.open('r');

while(! fileObj.eof) {
var currentLine = fileObj.readln();
timings.push(currentLine);
}
fileObj.close();
}
catch (errMain) {
}
return timings;
}