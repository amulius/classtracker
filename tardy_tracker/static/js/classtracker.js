/**
 * Created by Adam on 10/14/14.
 */

$(document).ready(function() {

    $('#checkIn').on('click', function () {
        console.log("hi");
        currentUser = $('#currentUser').text();
        currentCourse = $('#currentCourse').text();

        datas = {
            student: currentUser,
            course: currentCourse
        };

        console.log(datas);
        datas = JSON.stringify(datas);

        $.ajax({
            url: '/checkin/',
            type: 'POST',
            dataType: 'json',
            data: datas,
            success: function(response) {
                console.log(response);
                $('#checkIn').html("Checked In!");
            },
            error: function(response) {
                console.log(response);
            }
        });
    });

});
