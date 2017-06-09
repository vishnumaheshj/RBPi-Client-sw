/**
 * Created on 06/06/17.
 */
function processAndToggle(data) {
    // Dummy data1 to see working of javascript..
    var data1 = '{"_id": {"$oid": "5938405d23ea620c8afa93f4"}, "hubAddr": 72623859790382856, "board1": {"switch8": 4, "devIndex": 1, "switch3": 1, "lastModified": {"$date": 1496953485725}, "switch1": 1, "switch7": 4, "switch6": 4, "switch5": 4, "switch4": 0, "epStatus": 5, "switch2": 0, "type": 2}, "totalNodes": 1}'
    var jsonData = JSON.parse(data);
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

/*
{"_id": {"$oid": "5938405d23ea620c8afa93f4"}, "hubAddr": 72623859790382856, "board1": {"switch8": 4, "devIndex": 1, "switch3": 1, "lastModified": {"$date": 1496953485725}, "switch1": 1, "switch7": 4, "switch6": 4, "switch5": 4, "switch4": 0, "epStatus": 5, "switch2": 0, "type": 2}, "totalNodes": 1}
*/
$("[id^=user_msg]").submit(function(e) {

    e.preventDefault(); // avoid to execute the actual submit of the form.

    $.ajax({
           type: $(this).attr('method'),
           url:  $(this).attr('action'),
           data: $(this).serialize(), // serializes the form's elements.
           success: function(data)
           {
				processAndToggle(data);
           }
         });
});

