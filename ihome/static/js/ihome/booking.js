function hrefBack() {
    history.go(-1);
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

function showErrorMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

$(document).ready(function(){
    // TODO: 判断用户是否登录

    $(".input-daterange").datepicker({
        format: "yyyy-mm-dd",
        startDate: "today",
        language: "zh-CN",
        autoclose: true
    });
    $(".input-daterange").on("changeDate", function(){
        var startDate = $("#start-date").val();
        var endDate = $("#end-date").val();

        if (startDate && endDate && startDate > endDate) {
            showErrorMsg("日期有误，请重新选择!");
        } else {
            var sd = new Date(startDate);
            var ed = new Date(endDate);
            days = (ed - sd)/(1000*3600*24);
            var price = $(".house-text>p>span").html();
            var amount = days * parseFloat(price);
            $(".order-amount>span").html(amount.toFixed(2) + "(共"+ days +"晚)");
        }
    });
    var queryData = decodeQuery();
    var houseId = queryData["hid"];

    // 获取房屋的基本信息
    $.get("/api/v1.0/houses/" + houseId,function (resp) {
        if(resp.erron == "0"){
            $(".house-info>img").attr("src",resp.data.house.img_urls[0])
            $(".house-text>h3").html(resp.data.house.title)
            $(".house-info>p>span").html(resp.data.house.price)
        }
    })
    // 订单提交
    $(".submit-btn").on("click",function () {
        var start_date = $("#start-date").val()
        var end_date = $("#end-date").val()
        if(!(start_date&&end_date)){
            return
        }
        var params = {
            "start_date":start_date,
            "end_date":end_date,
            "hid":houseId
        }
        $.ajax({
            url:"/api/v1.0/orders",
            type:"post",
            data:JSON.stringify(params),
            headers:{
                "X-CSRFToken":getCookie("csrf_token")
            },
            contentType:"application/json",
            success:function (resp) {
                if(resp.erron == "0"){
                    location.href = "/orders.html"
                }else if(resp.erron == "4101"){
                    location.href = "/login.html"
                }else {
                    alert(resp.errmsg)
                }
            }



        })




    })
})
