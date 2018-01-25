$(document).ready(function() {

	// Show a notification to the user using bootstrap-notify
	function showNotification(message, type, icon){
		$.notify({
			message: message,
			icon: icon
		},{
			type: type,
			delay: 3000,
			animate: {
				enter: 'animated slideInDown',
				exit: 'animated slideOutUp'
				}
		});
	}

	// Elements buttons template
	var submit_tpl = '<button type="submit" class="btn editable-button btn-danger btn-xs"><span class="fa fa-check"></span><span class="sr-only">Save</span></button>';
	var cancel_tpl = '<button type="reset" class="btn editable-button btn-default btn-xs"><span class="fa fa-times"></span><span class="sr-only">Cancel</span></button>';
	var enabledEl = '<span class="fa fa-check"></span>';
	var disabledEl = '<span class="fa fa-times"></span>';
	
	// Hidden button for a11y.
	$('.edit-a11y-btn').click(function(){
		$(this).next('.editable-content')[0].click();
	});

	// Special display values for some elements
	function setupElement(el, settings){
		switch (settings.type) {
			case 'select':
				return $(el).html(settings.data[settings.data.selected]);
			case 'checkbox':
				return $(el).html(settings.value?enabledEl:disabledEl);
		}
	}

	// Editable elements
	$('span.editable-content').each(function(el){
		var data = $(this).data();
		options = {
			type: data.type,
			name: data.name,
			url: data.url,
			value: data.value,
			label: data.label,
			data: data.choices,
			onblur: 'ignore',
			cssclass: 'inline-edit-form',
			cols: 20,
			rows: 8,
			submit: submit_tpl,
			cancel: cancel_tpl
		}

		// Callback after submiting content
		options.callback = function(value, settings){
			$(this).attr('tabindex', -1).focus();
			switch (settings.type) {
				case 'select':
					return $(this).html(settings.data[value]);
				case 'checkbox':
					return $(this).html(JSON.parse(value)?enabledEl:disabledEl);
			}
		}
		
		// Setup the initial display values
		setupElement(this, options);
		
		// invoke the plugin on this element.
		$(this).editable(submit_editable, options);
		
		// A Custom submit hook.
		function submit_editable(value, settings){
			var name = settings.name;
			var submit_data = {};
			var retval = value;
			submit_data[name] = value;
			$.ajax({
				type: 'PUT',
				url: settings.url,
				data: submit_data,
				success: function(resp){
					retval = resp[name];
					if (name==='title') {
						$('title').text(retval);
					} else if (name==='slug'){
						location.replace(resp.site_url);
					}
					showNotification('The changes persisted to the server.', 'info', 'fa fa-info-circle');
				},
				error: function(e){
					showNotification('Error submitting data to the server.', 'warning', 'fa fa-warning');
				}
			});
			return retval;
		};

	});
});