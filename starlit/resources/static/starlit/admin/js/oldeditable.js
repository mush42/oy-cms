$(document).ready(function() {
	$.fn.editable.defaults.ajaxOptions = {type: "PUT"};
	$.fn.editableform.buttons = '<button type="submit" class="btn editable-submit btn-sm btn-primary"><span class="fa fa-check"></span></button><button type="button" class="btn editable-cancel btn-default btn-sm"><span class="fa fa-times"></span></button>';
	$('.editable-trigger').each(function(el){
		$(this).hover(function(e){
			$(this).prev('.editable-content').css('background', 'rgba(150, 150, 150, .3)');
		},
		function(e) {
			$(this).prev('.editable-content').css('background', 'transparent');
		});
		options = {
			placement: 'bottom',
			showbuttons: 'left',
			params: function(params){
				attr = params['name'];
				params[attr] = params.value;
				delete params.value;
				delete params.pk;
				return params;
			},
			success: function(response, newValue) {
				if(response.status == 'error') return response.message;
				if(response.site_url) {
					location.replace(response.site_url);
				} else {
					location.reload()
				}
			},
			error: function(resp, val){
				if (resp.status >=500){
					alert("Server Error");
				}
				return resp.responseText;
			}
		};
		if ($(this).attr('data-type') == 'textarea'){
			options.tpl = '<textarea class="mceEditor"></textarea>';
		}
		$(this).click(function(e){
			tinyMCE.execCommand("mceAddEditor", false, document.querySelector('.mceEditor'));
		});
		$(this).editable(options);
	});
});