(function( $ ) {

var proto = $.ui.autocomplete.prototype,
  initSource = proto._initSource;

function filter( array, term ) {
  var matcher = new RegExp( $.ui.autocomplete.escapeRegex(term), "i" );
  return $.grep( array, function(value) {
    return matcher.test( $( "<div>" ).html( value.label || value.value || value ).text() );
  });
}

$.extend( proto, {
  _initSource: function() {
    if ( this.options.html && $.isArray(this.options.source) ) {
      this.source = function( request, response ) {
        response( filter( this.options.source, request.term ) );
      };
    } else {
      initSource.call( this );
    }
  },

  _renderItem: function( ul, item) {
    return $( "<li></li>" )
      .data( "item.autocomplete", item )
      .append( $( "<a></a>" )[ this.options.html ? "html" : "text" ]( item.label ) )
      .appendTo( ul );
  }
});

})( jQuery );

var highlightSearchText = function(value){
  var re = new RegExp('(' + $("#companySearch").val() + ')', "gi");
  return value.replace(re, '<b>$1</b>');
}

var translatePartyType = function(value){
  switch(value){
    case 'cm':
      return 'Council Member';
    case 'cl':
      return 'Council Applicant';
    case 'ca':
      return 'Council Lead';
  }
}

var translateJob = function(title, company){
  if (title == null)
    title = '';
  if (company == null)
    company = '';

  if (title.length == 0)
    return company;

  if (company.length == 0)
    return title;

  return title + ', <b>' + company + '</b>';
}

$(function() {
  $( "#companySearch" ).autocomplete({
    source: function( request, response ) {
      $.ajax({
        url: "/search/" + $("input:radio[name=rdo_search]:checked").val(),
        dataType: "jsonp",
        data: {
          featureClass: "P",
          style: "full",
          maxRows: 12,
          name_contains: request.term
        },
        success: function( data ) {
          if ($("input:radio[name=rdo_search]:checked").val() == 'company'){
            var len3 = 0;
            var len4 = 0;
            $.map( data.res_data, function( item ) {
              var name = item[1];
              var exchange = item[4] == null ? '' : item[4];
              var ticker = item[3] == null ? '' : item[3];
              if (item[3] != null && item[3].length > len3)
                len3 = item[3].length;
              if (item[4] != null && item[4].length > len4)
                len4 = item[4].length;
            });
            len3 = len3 * 1.1 ;
            len4 = len4 ;
            response( $.map( data.res_data, function( item ) {
              return {
                label: '<div style="white-space:nowrap;"><div style="float:left;padding-right:5px;">' + highlightSearchText(item[1]) + '</div><div style="width:' + len4 + 'em;float:right;padding-left:5px;">' + (item[4] == null ? '&nbsp;' : item[4]) + '</div><div style="width:' + len3 + 'em;float:right;padding-left:5px;padding-right:5px;">' + highlightSearchText(item[3] == null ? '&nbsp;' : item[3]) + '</div>&nbsp;</div>',
                value: item[1],
                id: item[0],
              }
            }));
          }
          else{
            var len3 = 0;
            var len4 = 0;
            $.map( data.res_data, function( item ) {
              var name = item[1];
              job = translateJob(item[4], item[5]);
              var partyType = translatePartyType(item[3]);
              if (partyType.length > len3)
                len3 = partyType.length;
              if (job.length > len4)
                len4 = job.length;
            });
            len3 = len3 * .6;
            len4 = len4 * .5;
            response( $.map( data.res_data, function( item ) {
              job = translateJob(item[4], item[5]);
              return {
                label: '<div style="white-space:nowrap;"><div style="float:left;padding-right:5px;">' + highlightSearchText(item[1]) + '</div><div style="width:' + len3 + 'em;float:right;padding-left:5px;padding-right:5px;">' + translatePartyType(item[3]) + '</div><div style="width:' + len4 + 'em;float:right;padding-left:5px;padding-right:5px;overflow-x:hidden;" title="' + job + '">' + job + '</div>&nbsp;</div>',
                value: item[1],
                id: item[0],
              }
            }));
          }
        }
      });
    },
    select: function(event, ui){
      reloadTreeWithId(ui.item.id);
    },
    minLength: 2,
    html: "html"
  });
});