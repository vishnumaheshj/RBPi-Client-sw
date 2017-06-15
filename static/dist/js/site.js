/**
 * Created on 06/06/17.
 */

function getCookie(name) {
var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
return r ? r[1] : undefined;
}

var globalSocketID = 0;

$('document').ready(function(){
    var sock = new SockJS(window.location.href+'socket');
    sock.onopen = function() {
        ;
    };

    sock.onmessage = function(e) {
        var data = JSON.parse(e.data);
        if (data['type'] == 'init') {
            globalSocketID = data['socketId'];

            var username = document.getElementById('username').value;
            //alert("user:"+username);
            msg =   {'type':'auth', 'socketId': globalSocketID, 'user': username,};
            sock.send(JSON.stringify(msg));
        }
        else if (data['serverPush'] == 'stateChange') {
            //alert("serverPush");
            if (data['socketId'] != globalSocketID) {
                //alert("Toggle");
                processAndToggle(data, 1);
            }
        }
        else {
            //alert(data);
        }
    };

    sock.onclose = function() {
        //alert('closed');
    };
});


function processAndToggle(data, json) {
    // Dummy data1 to see working of javascript..
    var data1 = '{"_id": {"$oid": "5938405d23ea620c8afa93f4"}, "hubAddr": 72623859790382856, "board1": {"switch8": 4, "devIndex": 1, "switch3": 1, "lastModified": {"$date": 1496953485725}, "switch1": 1, "switch7": 4, "switch6": 4, "switch5": 4, "switch4": 0, "epStatus": 5, "switch2": 0, "type": 2}, "totalNodes": 1}'
    if (!json) {
        var jsonData = JSON.parse(data);
    }
    else {
        var jsonData = data;
    }
    if (typeof(jsonData["hubAddr"]) != 'undefined')
    {
        var index;
        var i;
        var switches = ["switch1", "switch2", "switch3", "switch4", "switch5", "switch6", "switch7", "switch8"];

        for (board in jsonData)
        {
            if (board.substring(0,5) == 'board')
            {
                for (index = 0; index < switches.length; index++)
                {
                    if (typeof(jsonData[board][switches[index]]) != undefined)
                    {
                        if (jsonData[board][switches[index]] == 0x1)
                        {
                            // TODO: Check if such board/switch exist. if not, reload..
                            $('#' + board + switches[index]).bootstrapToggle('on')
                        }
                        else if (jsonData[board][switches[index]] == 0x0)
                        {
                            // TODO: Check if such board/switch exist. if not, reload..
                            $('#' + board + switches[index]).bootstrapToggle('off')
                        }
                    }
                }
            }
        }
    }
}


$("[id^=user_msg]").submit(function(e) {

    e.preventDefault(); // avoid to execute the actual submit of the form.
    var formData = $(this).serializeArray();
    formData.push({"name":"socketId","value":globalSocketID });

    $.ajax({
           type: $(this).attr('method'),
           url:  $(this).attr('action'),
           data: formData,
           headers: {
            "X-Xsrftoken": getCookie("_xsrf"),
            },
           success: function(data)
           {
                //$(this).find('.checkbox').removeClass('disabled');
                //$(this).find("[id^=board]").prop('disabled', false);
                processAndToggle(data, 0);
                $('.row').removeClass("disabledbutton");
                document.getElementById('modal').style.display = 'none';

           }
         });

    //$(this).find('.checkbox').addClass('disabled');
    //$(this).find("[id^=board]").prop('disabled', true);
    $('.row').addClass("disabledbutton");
    document.getElementById('modal').style.display = 'block';
});

