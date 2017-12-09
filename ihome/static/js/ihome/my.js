function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

// TODO: 点击推出按钮时执行的函数
function logout() {

}

$(document).ready(function(){

    // 在页面加载完毕之后去加载个人信息
     $.get("/api/v1.0/user",function (resp) {
        if (resp.erron == "0"){
            $("#user-avatar").attr("src",resp.data.avatar_url)
            $("#user-name").html(resp.data.name)
            $("#user-mobile").html(resp.data.mobile)
        }else if(resp.erron=="4101"){
            location.href = "/login.html"
        }
    })

});
