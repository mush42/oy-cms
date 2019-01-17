$(function() {

  ClassicEditor
    .create( document.querySelector('.ckeditor'))
    .catch( error => {
        console.error( error );
  });

});