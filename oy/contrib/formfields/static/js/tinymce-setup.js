$(function() {
  tinymce.init({
    selector: ".tinymce",
	setup: function (editor) {
		editor.on('change', function (e) {
			editor.save();
		});
	}

  });
});