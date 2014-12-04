
var DetailPanel = {
	isActive: false,
	loadDetail:function(partyId) {

		this.partyId = partyId;
		var that = this;
		url = "/expertDetail/" + this.partyId + "?callback=?"
		
		$('#detail-waiting').show();
		
		jQuery.getJSON(url, function(data) { 

			var expertDetail = data.res_data;
			this.currentDetail = expertDetail;

			var moreLink = " <a href='javascript:DetailPanel.displayFullDetails();'>more...</a>"
			that.name = expertDetail.name;
			
			that.biography = expertDetail.bio == null ? "Biography not available" : expertDetail.bio;
			var biography = expertDetail.bio != null ? (that.biography.substring(0,250) + "...<br/>" + moreLink) : that.biography;
			that.jobs = formatJobHistory(expertDetail.jobHistory);
			that.sourceId = expertDetail.sourceId;

			
			$('#detailContainer').slideUp(function() {
				$("#detailContainer").html(
					$('#expertDetail').html()
						.replace(/_NAME_/g, that.name)
						.replace(/_JOB_HISTORY_/g, that.jobs + "<br/>")
						.replace(/_BIO_/g, biography + "<br/>")
						.replace(/_SOURCE_ID_/g, that.sourceId)
						.replace(/_NODE_ID_/g, that.partyId)
						.replace(/_VEGA_URL_/g, config.vegaRoot)
					);
				$('#detail-waiting').hide();
				$('#detailContainer').slideDown();
			});

		});
	},
	displayFullDetails:function(expertObject) {
		this.isActive = true;
		$('#detailPanel').css('z-index',90);
		$('#darkClass').show();
		if ($.browser.msie && jQuery.browser.version == '8.0'){
			jQuery("#detailPanel").show();
		}
		else{
        	jQuery("#detailPanel").show("drop", { direction: "right" }, 600);
        }

		$("#panelhtml").html(
				$('#expertDetail').html()
					.replace(/_NAME_/g, this.name)
					.replace(/_JOB_HISTORY_/g, this.jobs + "<br/>")
					.replace(/_BIO_/g, this.biography + "<br/>")
					.replace(/_SOURCE_ID_/g, this.sourceId)
					.replace(/_NODE_ID_/g, this.partyId)
					.replace(/_VEGA_URL_/g, config.vegaRoot)
				);
		$('#expertDetailInner').css({'border':'0px', 'background-color':'#ffffff'});
	},
	clearDetail: function() {
		if(!$('#detailContainer').is(":hidden")) {
			$('#detailContainer').slideUp( function(){
				$('#detailContainer').html("");
			});
		}
	},
	closePanel: function() {
		if(DetailPanel.isActive) {
			if ($.browser.msie && jQuery.browser.version == '8.0')
				$("#detailPanel").hide();
			else
	    		$("#detailPanel").hide("drop", { direction: "right" }, 400);
	    	$("#panelhtml").html("");
	    	this.isActive = false;
	    	$('#darkClass').hide();
	    }

  	},
  	jumpFromChartToNode: function(nodeId) {
      reloadTreeWithId(nodeId);
      this.closePanel();
  }
};