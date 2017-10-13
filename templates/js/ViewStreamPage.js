$(function(){

var dz = $("#upform")[0].dropzone
var dzOptions = dz.options;

// wait until press submit
dzOptions.autoProcessQueue = false

// allow up to 5 files
dzOptions.parallelUploads = 5
dzOptions.maxFiles = 5
dzOptions.uploadMultiple = true

// process upload queue when press submit button

$("#dzUploadSubmit").click(function(e){
    dz.processQueue();
});

});