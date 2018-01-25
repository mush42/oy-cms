var __file_browser_params;
var __current_popup;

$(document).ready(function() {
	// Start This Module
	
	function get_el_by_name(el, identifier){
		return $('#' + $(el).data('name') + identifier);
	};
	
	$('.file-input').each(function(){
		value = $(this).val();
		if (value){
			var source = window.__images_base_url + value;
			get_el_by_name(this, '-image').attr('src', source);
			get_el_by_name(this, '-preview').fadeIn({duration:500, easing:'swing'});
		}
	});

	// Removing the image.
	$('.remove-file').click(function(){
		get_el_by_name(this, '').val('');
		get_el_by_name(this, '-preview').fadeOut({duration:500, easing:'swing'});
	});
	
	// Selecting the image
	$('.image-select').click(function(){
		if (__current_popup){
			__current_popup.close();
		};
		__file_browser_params = {
			input: get_el_by_name(this, ''),
			preview: get_el_by_name(this, '-preview'),
			image: get_el_by_name(this, '-image')
		};
		__current_popup = lity($(this).data('target-url') + '?popup=1&type=image');
	})
	
	// End This Module
});