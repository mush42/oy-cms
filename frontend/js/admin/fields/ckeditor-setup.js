$(function() {

  ClassicEditor
    .create( document.querySelector('.ckeditor'))
    .catch(function(error) {
        console.error( error );
  });

});