var basketItem = function(id, partyId, name){
	this.id = id;
	this.partyId = partyId;
	this.name = name;
}
var basket = {
	councilMembers: [],
	target: null,
	add: function(councilMemberId, partyId, councilMemberName)
		{
			//Do not add duplicates
			for (i = 0; i < this.councilMembers.length; i++){
				if (this.councilMembers[i].id == councilMemberId){
					return;
				}
			}
			var item = new basketItem(councilMemberId, partyId, councilMemberName);
			this.councilMembers.push(item);
			this.refresh();
		},
	remove: function(councilMemberId)
		{
			for (i = 0; i < this.councilMembers.length; i++){
				if (this.councilMembers[i].id == councilMemberId){
					this.councilMembers.splice(i, 1);
				}
			}
			this.refresh();
		},
	refresh: function()
		{
			basketContent = '<h2 class="basketHeader">Expert Basket</h2>';
			basketContent += '<div class="basketContainer">'

			if (this.councilMembers.length == 0){
				basketContent += 'Select a council member,<br/>then click Add To Basket';
			}
			else{
				for (i = 0; i < this.councilMembers.length; i++){
					basketContent += '<div><input class="basketRemoveButton" type="button" onclick="basket.remove(' + this.councilMembers[i].id + ')">&nbsp;' + this.councilMembers[i].name + '</div>';
				}
			}
			basketContent += '</div>';
			if (this.councilMembers.length > 0)
				basketContent += '<div style="text-align:center">' +
								'<input type="button" value="Add to Consultation" onClick="basket.addToConsultation();"></div>';
			this.target.html(basketContent);
			this.persist();
		},
	clear: function()
		{
			this.councilMembers = [];
			this.refresh();
		},
	addToConsultation: function()
		{
			var list = [];
			for (i = 0; i < this.councilMembers.length; i++){
				list.push(this.councilMembers[i].id);
			}

			window.open('http://' + config.vegaRoot + '/Consult/Meeting/AddToMeeting.aspx?ids=' + list.join(','));
			this.clear();
		},
	partyIdList : function()
		{
			var list = [];
			for (i = 0; i < this.councilMembers.length; i++){
				list.push(this.councilMembers[i].partyId);
			}

			return list.join(',')
		},
	persist : function()
		{
			if (this.councilMembers.length == 0)
				$.cookie("basket", null, { expires: -10 });
			else{
				var data = [];
				for (i = 0; i < this.councilMembers.length; i++){
					var cm = this.councilMembers[i];
					data.push(cm.id + "~~" + cm.partyId + "~~" + cm.name);
				}
				$.cookie("basket", data.join("||"), { expires: 1});
			}
		},
	retrieve : function()
		{
			var data = $.cookie("basket");
			if (data == null) return;

			var lines = data.split("||");
			for (i = 0; i < lines.length; i++){
				items = lines[i].split("~~");
				var item = new basketItem(items[0], items[1], items[2]);
				this.councilMembers.push(item);
			}
		}
}

$(document).ready(function() {
	basket.retrieve();
	basket.refresh();
})

