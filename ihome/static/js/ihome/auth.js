function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}


function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    // 查询用户的实名认证信息
    $.get("/api/v1.0/user/auth",function (reps) {
        if(reps.erron=="0"){
            // 判断是否有认证信息，如果有将保存按钮隐藏和输入框置为不可用
            if(reps.data.real_name && reps.data.id_card){
                //进行显示
                $("#user-name").val(reps.data.real_name)
                $("#id-card").val(reps.data.id_card)
                // 将保存按钮隐藏和输入框置为不可用
                $(".btn-success").hide()
                $("#user-name").prop("disabled",true)
                $("#id-card").prop("disabled",true)
            }else if(reps.erron=="4101"){
                location.href = "/login.html"
            }else {
                alert(reps.errmsg)
            }

        }
    })

    // TODO: 管理实名信息表单的提交行为

})