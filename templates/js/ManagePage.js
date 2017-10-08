
// AJAX TABLE POPULATE
function management_call(){
    var userID = $('meta[name=userID]').attr("content");
    var url = "services/management?userID="+userID
    var jqxhr = $.getJSON( url )
      .done(function( management_data ) {
        // fill in owned table with management_data.owned_streams
        // load owned streams
        var info_url = "services/streaminfo?streamID="+ encodeURIComponent(JSON.stringify(management_data.owned_streams))
        $.getJSON( info_url ).done(function( stream_data ){
            for(i=0; i<stream_data.length; i++){
                var newrow = makeOwnedTableRow(stream_data[i]).hide()
                $('#ownedtable tr:last').after(newrow)
                newrow.fadeIn()
            }
            $('#deleteform').find('.loader').fadeOut().remove()
            $('#ownedtable').find('.checkbox-div').click(toggleCheck);
        });

        // fill in owned table with management_data.subscribed_streams
        // load subscribed streams
        var info_url = "services/streaminfo?streamID="+ encodeURIComponent(JSON.stringify(management_data.subscribed_streams))
        $.getJSON( info_url ).done(function( stream_data ){
        for(i=0; i<stream_data.length; i++){
                var newrow = makeSubscribedTableRow(stream_data[i]).hide()
                $('#subscribedtable tr:last').after(newrow)
                newrow.fadeIn()
            }
            $('#unsubscribeform').find('.loader').fadeOut().remove()
            $('#subscribedtable').find('.checkbox-div').click(toggleCheck);
        });
      })
      .fail(function( jqxhr, textStatus, error ) {
        var err = textStatus + ", " + error;
        alert( "Request Failed: " + err );
    });
}

function makeSubscribedTableRow(stream){
    var date = new Date(stream.newestDate);
    if(isNaN(date.getTime()))
        date = "";
    else
        date = date.toDateString();
    var tr = $('<tr>', {class: 'datarow'})
                .append($('<td>')
                    .append('<a href="/viewstream?streamID=' + stream.id + '">' + stream.name + '</a>'))
                .append($('<td>')
                    .text(date))
                .append($('<td>')
                    .text(stream.numItems))
                .append($('<td>')
                    .text(stream.numViews))
                .append(makeDeleteCheckBoxTD(stream.id, stream.name, 'unsubscribe'))
    return tr
}

function makeOwnedTableRow(stream){
    var date = new Date(stream.newestDate);
    if(isNaN(date.getTime()))
        date = "";
    else
        date = date.toDateString();
    var tr = $('<tr>')
                .append($('<td>')
                    .append('<a href="/viewstream?streamID=' + stream.id + '">' + stream.name + '</a>'))
                .append($('<td>')
                    .text(date))
                .append($('<td>')
                    .text(stream.numItems))
                .append(makeDeleteCheckBoxTD(stream.id, stream.name, 'delete'))
    return tr
}

function makeDeleteCheckBoxTD(streamID, streamName, boxclass){
    var td = $('<td>')
                .attr('class', "delete-col checkbox-div")
                .append($('<div />', {
                    class: "checkbox " + boxclass,
                    id: boxclass + '_' + streamID
                    })
                    .attr('name', streamName)
                    .attr('data-type', boxclass))
    return td
}
// END AJAX STUFF

// toggle the checked state of a box
// also set disabled property of associated button if needed
// (matched by data-type in the checkbox and class in the button)
function toggleCheck(){
    $(this).find('.checkbox').toggleClass('checked')
    $(this).closest('tr').toggleClass('stream-checked')

    isChecked = $(this).hasClass('checked')

    if( !isChecked )
        $(this).closest('table').find('.check_all').removeClass('checked')

    // check if all are not checked
    type = $(this).find('.checkbox').data("type")
    anyChecked = $('.checked.'+type).length>0
    $('.mybtn.'+type).prop('disabled', !anyChecked)
}


// force checked state of a checkbox. No button disabled property check
function forceCheck(){
    $(this).find('.checkbox').addClass('checked')
    $(this).closest('tr').addClass('stream-checked')
}


// force unchecked state of a checkbox. No button disabled property check
function forceUncheck(){
    $(this).find('.checkbox').removeClass('checked')
    $(this).closest('tr').removeClass('stream-checked')
}


// set all boxes in a column to checked, and set button disabled property
function columnCheck(){
    $(this).toggleClass('checked')
    all_boxes = $(this).closest('table').find('.checkbox-div')
    isChecked = $(this).hasClass('checked')
    type = $(this).data("type")
    $('.mybtn.'+type).prop('disabled', !isChecked)
    if( isChecked )
        all_boxes.each(forceCheck)
    else
        all_boxes.each(forceUncheck)
}


$(document).ready(function(){

    management_call();

    // fade out message bar
    $("#message").delay(3000).slideUp(500)
                  .animate(
                    { opacity: 0 },
                    { queue: false, duration: 3500 }
                  );

    // change from checked to unchecked and vice versa
    $('.check_all').click(columnCheck)

    // delete button click
    // add items to form data
    $('#delete_button').click(function(){
        deleted = $('#ownedtable').find('.checked')
        ids = deleted.map(function() { return $(this).attr('id'); }).get();
        names = deleted.map(function() { return $(this).attr('name'); }).get();
        rows = deleted.map(function() { return $(this).closest('tr'); }).get();
        all = $('#ownedtable').find('.check_all').hasClass('checked');

        // add items to the form
        for(i=0; i<ids.length; i++){
                id = String(ids[i]).replace('delete_','')
        }

        ids = JSON.stringify(ids)
        names = JSON.stringify(names)

        id_input = $("<input>").attr("type", "hidden").attr("name", "streamID").val(ids);
        name_input = $("<input>").attr("type", "hidden").attr("name", "streamname").val(names);

        $('#deleteform').append(id_input)
        $('#deleteform').append(name_input)
    });

    // unsubscribe button click
    // add items to form data
    $('#unsubscribe_button').click(function(){
        deleted = $('#subscribedtable').find('.checked')
        ids = deleted.map(function() { return $(this).attr('id'); }).get();
        names = deleted.map(function() { return $(this).attr('name'); }).get();
        rows = deleted.map(function() { return $(this).closest('tr'); }).get();
        all = $('#subscribedtable').find('.check_all').hasClass('checked');

        // add items to the form
        for(i=0; i<ids.length; i++){
                id = String(ids[i]).replace('unsubscribe_','')
        }

        ids = JSON.stringify(ids)
        names = JSON.stringify(names)

        id_input = $("<input>").attr("type", "hidden").attr("name", "streamID").val(ids);
        name_input = $("<input>").attr("type", "hidden").attr("name", "streamname").val(names);

        $('#unsubscribeform').append(id_input)
        $('#unsubscribeform').append(name_input)
    });

});