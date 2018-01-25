$(document).ready(function() {
	
	$('a[title]:not([data-toggle])').each(function(){
		$(this).attr('aria-label', $(this).title);
		$(this).tooltip({
			placement: 'bottom',
			title: $(this).title,
		});
	})
});