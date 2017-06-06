/**
 * Created on 06/06/17.
 */


$("#user_msg").submit(function(e) {

    $.ajax({
           type: $(this).attr('method'),
           url:  $(this).attr('action'),
           data: $(this).serialize(), // serializes the form's elements.
           success: function(data)
           {
               alert(data); // show response from the server.
           }
         });

    e.preventDefault(); // avoid to execute the actual submit of the form.
});