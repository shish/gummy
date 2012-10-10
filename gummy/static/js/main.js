$(function() {
	$(".diff").each(function(i, el) {
		$(el).find(".diff-toggle").click(function() {
			$(el).find(".diff-content").toggle();
		});
	});
	if($.cookie('username')) {
		$("INPUT[name='author']").val($.cookie('username'));
	}
	$("INPUT[name='author']").change(function() {
		console.log("Username saved as", $(this).val());
		$.cookie('username', $(this).val(), {path: '/'});
	});
});
