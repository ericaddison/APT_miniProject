$(document).ready(function(){

    searchbar = $('#search_tags');

    // when key pressed, make text black and remove "search"
    searchbar.keydown(function(event) {
        if( event.keyCode == 13){
            $('#searchSubmit').click();
            return;
        }
    });

    // autocomplete function from jquery-ui
        var cache = {};
        searchbar.autocomplete({
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