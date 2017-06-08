/**
 * Created on 06/06/17.
 */

/*
{"_id": {"$oid": "5938405d23ea620c8afa93f4"}, "hubAddr": 72623859790382856, "board1": {"switch8": 4, "devIndex": 1, "switch3": 0, "lastModified": {"$date": 1496953485725}, "switch1": 0, "switch7": 4, "switch6": 4, "switch5": 4, "switch4": 0, "epStatus": 5, "switch2": 0, "type": 2}, "totalNodes": 1}
*/
$("[id^=user_msg]").submit(function(e) {

    $.ajax({
           type: $(this).attr('method'),
           url:  $(this).attr('action'),
           data: $(this).serialize(), // serializes the form's elements.
           success: function(data)
           {
				alert(data); // show response from the server.
				var json = JSON.parse(data);
				//if (json["switch1"]
           }
         });

    e.preventDefault(); // avoid to execute the actual submit of the form.
});

