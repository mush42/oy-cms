$(function() {

  var allEditors = document.querySelectorAll("textarea.ckeditor")

  for (var i = 0; i < allEditors.length; ++i) {
    ClassicEditor
      .create(allEditors[i])
      .catch(function(error) {
          console.error( error );
    });
  }

});