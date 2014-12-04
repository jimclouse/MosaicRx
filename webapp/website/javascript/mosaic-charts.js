/* ###########################
  * pie chart component
  * ########################## */  
  var mosPie; // needed for the Raphael reference: TODO: should put all of the grpah stuff in an object in separate file
  var loadPieChart = function(relationshipType) {

    url = "/relationDetail?nodeId=" + hyperTree.centralNodeId + 
          "&type=" + relationshipType + 
          "&callback=?"; 
    /* note that the order is super important. The items in values, legend, and links must
    be added in the same order as each other and include placeholers if empty */
    var Values = new Array();
    var Legends = new Array();
    var Links = new Array();

    currentNode = hyperTree.getCurrentNode();

    jQuery.getJSON(url, function(data) { 
        d = data.res_data;
        if( d.length > 0) { // look for empty array in returned json
            $.each ( d, function(index, value) {
                if(value["id"]) {
                    Links.push("javascript:DetailPanel.jumpFromChartToNode(" + value["id"] + ")")
                }
                else {
                  Links.push(null);
                }
                Legends.push("%%.% - " + value["name"])
                Values.push(value["value"])
            });

            // move panel into view
            DetailPanel.isActive = true;
            
            $('#detailPanel').css('z-index',90);
            $('#darkClass').show();
            if ($.browser.msie && jQuery.browser.version == '8.0')
              jQuery("#detailPanel").show();
            else{
              jQuery("#detailPanel").show("drop", { direction: "right" }, 600);
            }
            // begin loading pie chart
            mosPie = Raphael("panelhtml"),
              mpie = mosPie.piechart(180, 240, 100, Values, { 
                        legend: Legends, 
                        legendpos: "east",
                        href: Links
                        });

            mosPie.text(320, 100, "Revenue percent from customers for \n" + currentNode.name).attr({ font: "20px sans-serif" });

            mpie.hover(function () {
                          this.sector.stop();
                          this.sector.scale(1.1, 1.1, this.cx, this.cy);

                          if (this.label) {
                              this.label[0].stop();
                              this.label[0].attr({ r: 7.5 });
                              this.label[1].attr({ "font-weight": 800 });
                          }
                      }, function () {
                          this.sector.animate({ transform: 's1 1 ' + this.cx + ' ' + this.cy }, 500, "bounce");

                          if (this.label) {
                              this.label[0].animate({ r: 5 }, 500, "bounce");
                              this.label[1].attr({ "font-weight": 400 });
                          }
                      });
          }
          else {
              $('#darkClass').show();
              h = $('#detailPanel').html()
              $("#detailPanel").html(h + "Revenue Statistics not available for " + currentNode.name)
              $('#detailPanel').css('z-index',90);
              if ($.browser.msie && jQuery.browser.version == '8.0')
                $("#detailPanel").show();
              else
                $("#detailPanel").show("drop", { direction: "right" }, 600);
          }

      });
  }