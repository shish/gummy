$(function() {
	$(".diff").each(function(i, el) {
		$(el).find(".diff-toggle").click(function() {
			$(el).find(".diff-content").toggle();
		});
	});
});
