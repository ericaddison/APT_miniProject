
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

    // fade out message bar
    $("#message").delay(3000).slideUp(500)
                  .animate(
                    { opacity: 0 },
                    { queue: false, duration: 3500 }
                  );

    // change from checked to unchecked and vice versa
    $('.checkbox-div').click(toggleCheck);
    $('.check_all').click(columnCheck)

    // delete button click
    // add items to form data
    $('#delete_button').click(function(){
        deleted = $('#deletetable').find('.checked')
        ids = deleted.map(function() { return $(this).attr('id'); }).get();
        names = deleted.map(function() { return $(this).attr('name'); }).get();
        rows = deleted.map(function() { return $(this).closest('tr'); }).get();
        all = $('#deletetable').find('.check_all').hasClass('checked');

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

});