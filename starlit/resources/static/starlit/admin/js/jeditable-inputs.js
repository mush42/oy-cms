$(document).ready(function() {

// Number input
$.editable.addInputType('number', {
    element : function(settings, original) {
        var input = $('<input type="number">');
        $(this).append(input);
        return(input);
    }
});

// Date only input
$.editable.addInputType('date', {
    element : function(settings, original) {
        var input = $('<input>');
        $(this).append(input);
        return(input);
    },
    plugin : function(settings, original) {
		var form = this;
		$("input", this).daterangepicker({
			timePicker: false,
			showDropdowns: true,
			singleDatePicker: true,
			format: "YYYY-MM-DD",
		}, function(start, end){
			$(form).submit();
		});
	}
});

// Time only input
$.editable.addInputType('time', {
    element : function(settings, original) {
        var input = $('<input>');
        $(this).append(input);
        return(input);
    },
	plugin : function(settings, original) {
		var form = this;
		dp = $("input", this).daterangepicker({
			timePicker: true,
			timePickerIncrement: 1,
			timePicker12Hour: false,
			showDropdowns: true,
			singleDatePicker: true,
			format: "HH:mm:ss",
		}, function(start, end){
			$(form).submit();
		});
		dp.data('daterangepicker').container.find('.calendar-date').hide();
		dp.on('showCalendar.daterangepicker', function (event, data) {
			var $container = data.container;
			$container.find('.calendar-date').remove();
		});
	}
});

// Date & Time input
$.editable.addInputType('datetime', {
    element : function(settings, original) {
        var input = $('<input>');
        $(this).append(input);
        return(input);
    },
	plugin : function(settings, original) {
		var form = this;
		$("input", this).daterangepicker({
			timePicker: true,
			timePickerIncrement: 1,
			timePicker12Hour: false,
			showDropdowns: true,
			singleDatePicker: true,
			format: "YYYY-MM-DD HH:mm:ss",
		}, function(start, end){
			$(form).submit();
		});
	}
});

// Checkbox
$.editable.addInputType('checkbox', {
    element : function(settings, original) {
        var input = $('<input type="hidden" />');
		var checkbox = $('<label for="' + settings.name + 'id"' + '>' + '<input type="checkbox" id="' + settings.name + 'id"' + '/>' + settings.label + '</label>');
		$(this).append(checkbox);
		$(this).append(input);
        return(input);
    },
	content: function(string, settings, original){
		$(this).find('input[type="checkbox"]')[0].checked = settings.value;
	},
	submit: function(settings, original){
		var checkbox = $(this).find('input[type="checkbox"]')[0];
		var input = $(this).find('input[type="hidden"]')[0];
		$(input).val(JSON.stringify(checkbox.checked));
		settings.value = checkbox.checked;
	}
});

// TinyMCE WYSIWYG
$.editable.addInputType('mce', {
    element:function (settings, original) {
        var textarea = $('<textarea id="' + $(original).attr("id") + '_mce"/>');
        if (settings.rows) {
            textarea.attr('rows', settings.rows);
        } else {
            textarea.height(settings.height);
        }
        if (settings.cols) {
            textarea.attr('cols', settings.cols);
        } else {
            textarea.width(settings.width);
        }
        $(this).append(textarea);
        return(textarea);
    },
    plugin:function (settings, original) {
        tinyMCE.execCommand("mceAddEditor", true, $(original).attr("id") + '_mce');
    },
    submit:function (settings, original) {
        tinyMCE.triggerSave();
        tinyMCE.execCommand("mceRemoveEditor", true, $(original).attr("id") + '_mce');
    },
    reset:function (settings, original) {
        tinyMCE.execCommand("mceRemoveEditor", true, $(original).attr("id") + '_mce');
        original.reset(this);
    }
});


});