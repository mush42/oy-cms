$(document).ready(function() {
	
	$('*[title]:not([data-toggle])').each(function(){
		$(this).tooltip({
			placement: 'bottom',
			title: $(this).title,
		});
	})
});