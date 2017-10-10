$(document).ready(function(){

    searchbar = $('#search_tags');

    // initial setting for search bar
    if( searchbar.val() == "" ){
        searchbar.addClass('noEntryYet')
        searchbar.val("--search--")
    }

    // when key pressed, make text black and remove "search"
    searchbar.keydown(function(event) {
        if( event.keyCode == 13){
            $('#searchSubmit').click();
            return;
        }

        if( $(this).hasClass('noEntryYet') && isPrintableChar(event.keyCode) ){
            $(this).val("")
            $(this).removeClass('noEntryYet')
        }
    });

    // when search bar is empty again, put the light-gray "search" back on
    // unless enter, then submit form
    searchbar.keyup(function() {
        if( $(this).val() == "" && !$(this).hasClass('noEntryYet') ){
            $(this).addClass('noEntryYet')
            $(this).val("--search--")
        }
    });

    // autocomplete function from jquery-ui
    $( function() {
        var cache = {};
        searchbar.autocomplete({
        source: function( request, response ) {
            if(searchbar.hasClass('noEntryYet'))
                return;
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

});

function isPrintableChar(keycode){
    var valid =
        (keycode > 47 && keycode < 58)   || // number keys
        keycode == 32 || keycode == 13   || // spacebar & return key(s) (if you want to allow carriage returns)
        (keycode > 64 && keycode < 91)   || // letter keys
        (keycode > 95 && keycode < 112)  || // numpad keys
        (keycode > 185 && keycode < 193) || // ;=,-./` (in order)
        (keycode > 218 && keycode < 223);   // [\]' (in order)

    return valid;
};