var labelType, useGradients, nativeTextSupport, animate;

(function() {
  var ua = navigator.userAgent,
      iStuff = ua.match(/iPhone/i) || ua.match(/iPad/i),
      typeOfCanvas = typeof HTMLCanvasElement,
      nativeCanvasSupport = (typeOfCanvas == 'object' || typeOfCanvas == 'function'),
      textSupport = nativeCanvasSupport 
        && (typeof document.createElement('canvas').getContext('2d').fillText == 'function');
  //I'm setting this based on the fact that ExCanvas provides text support for IE
  //and that as of today iPhone/iPad current text support is lame
  labelType = (!nativeCanvasSupport || (textSupport && !iStuff))? 'Native' : 'HTML';
  nativeTextSupport = labelType == 'Native';
  useGradients = nativeCanvasSupport;
  animate = !(iStuff || !nativeCanvasSupport);
})();

var Log = {
  elem: false,
  write: function(text){
    if (!this.elem) 
      this.elem = document.getElementById('log');
    this.elem.innerHTML = text;
    this.elem.style.left = (500 - this.elem.offsetWidth / 2) + 'px';
  }
};

var formatJobHistory = function(historyObject) {
	var jobHistory = "";
		if (historyObject != null){
			for (i = 0; i < historyObject.length; i++){
				job = historyObject[i];
				jobHistory += job["title"] != "" ? job["title"] : "";
				jobHistory += job["company"] != "" && job["title"] != "" ? ", " : "";
				jobHistory += job["company"] != "" ?  "<a href='javascript:reloadTreeWithId(" + job["companyid"] + ");'>" + job["company"] + "</a>" : "";
				jobHistory += "<br/>";
				}
			}
	return jobHistory;
}
			
var hyperTree = {
    centralNodeId: "",
    centralNodeType: "",
    userFilterList: "",
    companyFilterList: "",
    personFilterList: "",
    nodeFilterList: "",
    continentFilterList: "",
    cmContinentFilterList: "",
    relationshipCount: 10,
    user_font_size: "0.8em",
    afterLoad: null,
    tip: {
        blocked:    false,
        nodeId:     null,
        hoverTimer: null,
        fadeTimer:  null
    },
    TIP_SHOW_PERIOD:  0,
    TIP_HIDE_PERIOD:  500,
    TIP_HOVER_PERIOD: 200,
    TIP_FADE_PERIOD:  400,
    LOCATION_INTERVAL: 0.20,
    MOVE_PERIOD: 750,

    getDataUrl:function(){
    	return "../sourceData.json";
    },
	reset:function(){
		DetailPanel.closePanel(); // close any flyout info box
		DetailPanel.clearDetail(); // clear any right hand detail data
		$('#infovis').html("");
    },
    getCurrentNode:function(){
		return this.ht.graph.getClosestNodeToOrigin("current");
    },
    loadData:function(){
		$.getJSON(this.getDataUrl(), function(data) {
			hyperTree.ht.loadJSON(data);
			hyperTree.ht.refresh(); //compute positions and plot.
			hyperTree.ht.controller.onComplete(); //end
		}).error(
			function (data) {
			    alert("Error loading graph data: " + data.responseText);
			}); 
    },
    /**
	 * Displays available information about a node in the panel
	 */
	showTip: function(node, block) {
	    if (hyperTree.ht.busy) { return; }
	    // check if this tip is already shown
	    if (hyperTree.tip.nodeId == node.id) { return; }
	    if (block) {
	        hyperTree.tip.blocked = true;
	    }

	    hyperTree.tip.nodeId = node.id;

	    var nodeElement = document.getElementById(node.id);
	    //alert(nodeElement.offsetWidth)


	    $('#tipPanel').stop();
	    $('#tipPanel').css('display', 'inline');

	    var tipContent = '';

		var debugInfo = config.web_debug ? "id: " + node.id + "<br/>" : ""; // web_debug in config.js
				
		var tickerData = '';
		// generate job history for applicable nodes
		var jobHistory = formatJobHistory(node.data.jobHistory);
		
		switch (node.data.classType)
		{
			case 'CM':
			case 'NONSTUDYCM':
				var toolTipDiv = '#councilMemberToolTip';
				break;
			case 'TRIAL':
				var toolTipDiv = '#trialToolTip';
				break;
			case 'applicant':
				var toolTipDiv = '#applicantToolTip';
				break;
			case 'person':
				var toolTipDiv = '#personToolTip';
				break;
			case 'company':
				var toolTipDiv = '#organizationToolTip';
				
				if (node.data.stockExchange != null)
					tickerData = node.data.stockExchange
				if (node.data.tickerSymbol != null){
					tickerData += (tickerData.length == 0 ? '' : ':') + node.data.tickerSymbol
					tickerData = '<a target="new" href="http://www.google.com/finance?q=' + tickerData + '">' + tickerData + '</a><br>'
				}
				break;
			case 'group':
				if(node.name == "Customers") {
					if (node.data.hasGraph) {
						toolTipDiv = '#customersToolTip';
						}
					else {
						toolTipDiv = '#customersNoDataToolTip';
					}
				}
				break;
			default:
				break;
		}

		// perform actual replacements now that we have all the data
		if (toolTipDiv != null) {
			tipContent = $(toolTipDiv).html()
				.replace(/NODE_NAME_JS/g, node.name.replace("'", "\\'"))
				.replace(/NODE_NAME/g, node.name)
				.replace(/VEGA_URL/g, config.vegaRoot)
				.replace(/NODE_ID/g, node.id)
				.replace(/_SOURCE_ID_/g, node.data.cmid)
				.replace(/_TRIALID_/g, node.data.NCT)
				.replace(/JOB_HISTORY/g, jobHistory)
				.replace(/CONTINENT/g, (node.data.continent == null || node.data.continent.length == 0) ? "Unknown" : node.data.continent)
				.replace(/DEBUG_INFO/g, debugInfo);
		}
		
	    $('#tipPanel').html(tipContent);

	    var left = parseInt(nodeElement.offsetLeft) + parseInt(nodeElement.offsetWidth) + 26;
	    var top = parseInt(nodeElement.offsetTop) + parseInt(nodeElement.offsetHeight) + 5;
	    if (nodeElement.offsetTop > 200)
	    	top += 5 - $('#tipPanel').height();

	    if(tipContent != "") {
		    $('#tipPanel').animate({
		        'opacity': 1,
		        'left': left,
		        'top': top
		    }, 200, function() {
		        hyperTree.tip.blocked = false;
		    });
		}
		else {
			$('#tipPanel').hide();
		}

	},

	/**
	 * Hides the tip panel
	 */
	hideTip: function(node)
	{
	    hyperTree.tip.nodeId = null;
	    $('#tipPanel').stop();
	    $('#tipPanel').animate({
	        'opacity': 0
	    }, hyperTree.TIP_HIDE_PERIOD, function() {
	        $('#tipPanel').css('display', 'none');
	    });

	},
	/**	
         * Initializes tip panel mouseover and mouseout effects
         */
	initPanel: function()
        {
            $('#tipPanel')
                .mouseover(function(e)
                {
                    if (hyperTree.tip.fadeTimer) {
                        clearTimeout(hyperTree.tip.fadeTimer);
                        hyperTree.fadeTimer = null;
                    }

                    if (hyperTree.tip.hoverTimer) {
                        clearTimeout(hyperTree.tip.hoverTimer);
                        hyperTree.tip.hoverTimer = null;
                    }
                })
                .mouseout(function(e)
                {
                    // high-priority tip is being displayed, don't fade
                    // out the tip
                    if (hyperTree.tip.blocked) {
                        return;
                    }

                    if (hyperTree.tip.hoverTimer) {
                        clearTimeout(hyperTree.tip.hoverTimer);
                        hyperTree.tip.hoverTimer = null;
                    }

                    if (hyperTree.tip.fadeTimer) {
                        clearTimeout(hyperTree.tip.fadeTimer);
                        hyperTree.tip.fadeTimer = null;
                    }

                    hyperTree.tip.fadeTimer = setTimeout(
                        function()
                        {
                            clearTimeout(hyperTree.tip.fadeTimer);
                            hyperTree.tip.fadeTimer = null;
                            hyperTree.hideTip();
                        }, hyperTree.TIP_FADE_PERIOD);
                });
        },
	initialize:function(){
		showHourGlass();
		// reset infovis size to match screen
		$("#center-container").width(($(window).innerWidth() - 400) + "px");
		
		var infovis = document.getElementById('infovis');
		var w = infovis.offsetWidth - 50, h = infovis.offsetHeight - 50;

		//init Hypertree
		hyperTree.ht = new $jit.Hypertree({
			//id of the visualization container
			duration:400,
			injectInto: 'infovis',
			//canvas width and height234324
			width: w,
			height: h,
			//Change node and edge styles such as
			//color, width and dimensions.
			Node: {
				overridable: true,
				dim: 6,
				//span: 2000,
				type: 'circle'
	  		},
	  		Edge: {
				//overridable: true
				lineWidth: 1,
				type: 'hyperline',
				color: "#5c5858"
	  		},
	  		onBeforeCompute: function(node){
	      		//Log.write("centering");
	  		},
			//Attach event handlers and add text to the
			//labels. This method is only triggered on label
			//creation
			onCreateLabel: function(label, node){
				label.id = node.id; 
				label.innerHTML = node.name;
				label.onclick = function(){
					DetailPanel.clearDetail();
			        hyperTree.ht.onClick(node.id, {
			        onComplete: function() {
			        	//hyperTree.ht.controller.GetMoreData(node);
			        	}
			    	}); 
				};
				// mouseover & out used for tooltips
				$(label)
					.mouseover(function(e)
                    {
                        // a high-priority tip is already being displayed,
                        // don't show this node's tip
                        if (hyperTree.tip.blocked) {
                            return;
                        }
                        if (hyperTree.tip.fadeTimer) {
                            clearTimeout(hyperTree.tip.fadeTimer);
                            hyperTree.fadeTimer = null;
                        }
                        clearTimeout(hyperTree.tip.hoverTimer);
                        hyperTree.tip.hoverTimer = null;
                        hyperTree.tip.hoverTimer = setTimeout(
                            function()
                            {
                                clearTimeout(hyperTree.tip.hoverTimer);
                                hyperTree.tip.hoverTimer = null;
                                hyperTree.showTip(node);
                            }, hyperTree.TIP_HOVER_PERIOD);
                    })
                    .mouseout(function(e)
                    {
                        // a high-priority tip is already being displayed,
                        // don't hide the tip
                        if (hyperTree.tip.blocked) {
                            return;
                        }
                        if (hyperTree.tip.hoverTimer) {
                            clearTimeout(hyperTree.tip.hoverTimer);
                            hyperTree.tip.hoverTimer = null;
                        }
                        clearTimeout(hyperTree.tip.fadeTimer);
                        hyperTree.tip.fadeTimer = null;
                        hyperTree.tip.fadeTimer = setTimeout(
                            function()
                            {
                                clearTimeout(hyperTree.tip.fadeTimer);
                                hyperTree.tip.fadeTimer = null;
                                hyperTree.hideTip();
                            }, hyperTree.TIP_FADE_PERIOD);
                    })
                    
			},
	  		GetMoreData: function(node) {
	  			if (node.data.classType == "group" || hyperTree.centralNodeId == node.id) return;

				showHourGlass();
				hyperTree.centralNodeId = node.id;

				jQuery.getJSON(hyperTree.getDataUrl(), function(data) { 
					hyperTree.ht.loadJSON(data.res_data);
					hyperTree.ht.refresh();
					hyperTree.ht.controller.onComplete();
                    }
		    	);
	  		},
			//Change node styles when labels are placed
			//or moved.
			onPlaceLabel: function(label, node){
				var style = label.style;
				style.display = '';
				style.family = "verdana, helvetica, arial";
				style.cursor = 'pointer';
				if (node._depth > 2) {
					style.display = 'none';
				}
				//used to center the label on the node
				var left = parseInt(style.left);
				var w = label.offsetWidth;
				style.left = (left - w / 2) + 'px';
				
			},
	  		onComplete: function(){
	      		hideHourGlass();

	      		//Set centralnode to translate id received via nodeId from querystring
	  			node = hyperTree.ht.graph.getClosestNodeToOrigin("current")
	  			hyperTree.centralNodeType = 'party';
	  			hyperTree.centralNodeId = node.id;

				if (hyperTree.afterLoad != null) {
					hyperTree.afterLoad(node);
				}
	  		}
		}); // end hyperTree.ht.create
	// load Json
	this.initPanel();
	this.loadData();

	} // end init		
} // end hypertree def


		
