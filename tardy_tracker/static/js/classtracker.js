/**
 * Created by Adam on 10/14/14.
 */

$(document).ready(function() {

    $('#checkIn').on('click', function () {


        //console.log("hi");
        currentUser = $('#currentUser').text();
        currentCourse = $('#currentCourse').text();
        console.log(currentUser,currentCourse,'User');

        datas = {
            "student": currentUser,
            "course": currentCourse
        };

        //console.log(datas);
        datas = JSON.stringify(datas);

        $.ajax({
            url: '/checkin/',
            type: 'POST',
           // dataType: 'json',
            data: datas,
            success: function(response) {
                console.log(response);
                if (response=="in") {
                    $('#pcheckin').html("Checked In!");
                    $("#checkIn").hide();
                }
                if (response=="already_in") {
                    $('#pcheckin').html("Already Checked In!");
                    $("#checkIn").hide();
                }
            },
            error: function(response) {
                console.log(response);
            }
        });
    });

});
