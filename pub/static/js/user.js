$(document).ready(function() {
    function gup( name ) {
        name = name.replace(/[\[]/,"\\\[").replace(/[\]]/,"\\\]");
        var regexS = "[\\?&]"+name+"=([^&#]*)";
        var regex = new RegExp( regexS );
        var results = regex.exec( window.location.href );
        if( results == null )
            return "";
        else
            return results[1];
    }

    function init() {
        // 添加一个图片上传的按钮，如果是update的话，这个按钮会在后面改变
		var user_ticket = $.parseHTML("<a href='/admin/userticketview?user_id="+gup('id')+"'>点击进入</a>");
		$("#ticket").replaceWith(user_ticket);
    }
    init();
});
