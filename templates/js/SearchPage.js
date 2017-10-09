$(document).ready(function(){

    $( function() {
        var cache = {};
        $( "#search_tags" ).autocomplete({
        source: function( request, response ) {
            var term = request.term;
            if ( term in cache ) {
              response( cache[ term ] );
              return;
            }

            $.getJSON( "services/autocomplete", request, function( data, status, xhr ) {
              cache[ term ] = data;
              response( data );
            });
            }
        })
    });


    $('#search_tags').keyup(function(event) {
        if(event.keyCode==13)
            $('#searchSubmit').click()
      });

});