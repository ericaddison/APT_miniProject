function toggleCheck(){
    $(this).find('.checkbox').toggleClass('unchecked')
    $(this).find('.checkbox').toggleClass('checked')
    $(this).closest('tr').toggleClass('stream-checked')
}

function checkAll(){
    $(this).find('.checkbox').removeClass('unchecked')
    $(this).find('.checkbox').addClass('checked')
    $(this).closest('tr').addClass('stream-checked')
}

function uncheckAll(){
    $(this).find('.checkbox').addClass('unchecked')
    $(this).find('.checkbox').removeClass('checked')
    $(this).closest('tr').removeClass('stream-checked')
}

function columnCheck(){
    $(this).toggleClass('checked')
    $(this).toggleClass('unchecked')
    all_boxes = $(this).closest('table').find('.checkbox-div')
    if( $(this).hasClass('checked') )
        all_boxes.each(checkAll)
    else
        all_boxes.each(uncheckAll)
}


$(document).ready(function(){

    // change from checked to unchecked and vice versa
    $('.checkbox-div').click(toggleCheck);

    $('#delete_all').click(columnCheck)

    // delete button click
    $('#delete').click(function(){
        deleted = $('#deletetable').find('.checked')
        ids = deleted.map(function() { return $(this).attr('name'); }).get();
        console.log(deleted.length)
        console.log(ids)
        // confirm delete
    });

    // onlick function for delete streams
    $.get( "test.php", function( data ) {
  alert( "Data Loaded: " + data );
});

});