(function($) {

	function get_window_params(){
		var parentWin = (window.frameElement && window.dialogArguments) || opener || parent || top;
		var params, editor;
		var tinymce = tinyMCE = parentWin.tinymce;
		if (tinymce){
			var editor = tinymce.EditorManager.activeEditor;
			if (editor){
				params = editor.windowManager.getParams();
			}
		}
		return {parent: parentWin, params: params, editor:editor};
	};
	
	// Display or hide the select file button based on the context
	(function(){
		var res = get_window_params();
		var has_parent = res.parent.__file_browser_params || res.params;
		if (!has_parent){
			$('.select-file').hide();
		} else {
			$('.side-nav').remove();
			$('.navbar').remove();
			$('#page-wrapper').addClass('full-width');
		}
	})()

	function file_submit(FileURL) {
		var res = get_window_params();
		res.parent.document.getElementById(res.params.input).value = FileURL;
		res.editor.windowManager.close(res.parent);
	};

	$('.select-file').click(function(e){
		var res = get_window_params();
		var path = $(this).attr('data-path');
		if (!res.params){
			res.parent.__file_browser_params.input.val(path);
			res.parent.__file_browser_params.image.attr('src', window.__images_base_url + path);
			res.parent.__file_browser_params.preview.fadeIn({duration:600, easing:'swing'});
			res.parent.__current_popup.close();;
		} else {
			file_submit(path);
		}
	})

})(jQuery);