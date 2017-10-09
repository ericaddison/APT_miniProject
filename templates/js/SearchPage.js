$(document).ready(function(){

    $( function() {
        $( "#search_tags" ).autocomplete({
          source: "services/autocomplete"
        });
    } );


    $('#search_tags').keyup(function(event) {
        if(event.keyCode==13)
            $('#searchSubmit').click()
      });

});