var breadCrumb = {
	target: null,
	nodeHistory: [],
	currentPosition: null,
	addItem: function(node){
		if (node.data.classType == "group") return;

		if ((this.currentPosition != null) && (node.id == this.nodeHistory[this.currentPosition].id)){
			return;
		}

		if (this.currentPosition != null && (this.nodeHistory.length > this.currentPosition + 1) && (this.nodeHistory[this.currentPosition + 1].id == node.id)){
			this.currentPosition += 1;
			return;
		}
/*
		if (this.currentPosition != null && (this.currentPosition > 0) && (this.nodeHistory[this.currentPosition - 1].id == node.id)){
			this.currentPosition -= 1;
			return;
		}
*/
		if (this.currentPosition < this.nodeHistory.length - 1)
			this.nodeHistory = this.nodeHistory.splice(0, this.currentPosition + 1);
		this.nodeHistory.push(node);
		this.refresh();
		this.currentPosition = this.nodeHistory.length - 1;
	},

	refresh: function(){
		content = '';
		for (i = 0; i < this.nodeHistory.length; i++){
			node = this.nodeHistory[i];
			content += ' <span class="breadcrumbItem" onclick="breadCrumb.trackPosition(' + i + ');reloadTreeWithId(' + node.id + ');">' + node.name + '</span>&nbsp;&gt;&gt;&nbsp;';
		}
		this.target.html(content);
	},
	trackPosition: function(index){
		this.currentPosition = index;
	}
}