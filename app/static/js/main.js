(function($) {
    "use strict";

    var constraints = {
        video: true
    };

    $('#submit').click(function() { $("#username").tooltip('dispose'); })

    $('#camera').on('click', function(e) {
        // do something...
        let camera;

        if ($.isEmptyObject($("#username").val())) {
            $('#username').tooltip({
                title: 'Please fill out Username field',
                template: '<div class="tooltip"><div class="tooltip-arrow"></div><div class="tooltip-head"><h3><i class="fas fa-exclamation-circle"></i></h3></div><div class="tooltip-inner"></div></div>'
            });
            $('#username').tooltip('toggle');
        } else {
            $.ajax({
                url: '/cameramodal',
                success: function(data) {
                    //console.log(data);
                    $('body').append(data);
                    $('#cameraModal').modal({
                        backdrop: true,
                        show: true
                    });
                }
            });
        };

        // Attach the video stream to the video element and autoplay.
        //context.drawImage(player, 0, 0, canvas.width, canvas.height);
    });

    $(document).on('show.bs.modal', '#cameraModal', function() {
        getClientCamera();
    })

    function getClientCamera() {
        navigator.mediaDevices.getUserMedia(constraints).then((mediaStream) => {
            // <button id="capture">Capture</button>
            // <canvas id = "canvas" width = 320 height = 240 ></canvas>
            // 
            $('.modal-body').append(`<video id = "player" autoplay style = "width: 100%"></video><div id="wrap"><img src="static/img/icon/camera.png" class="capture"></div><div id = 'output' ></div>`);
            $('.capture').on('click', captureImage);
            const player = document.getElementById('player');
            player.srcObject = mediaStream;
        });
    }

    function captureImage() {
        var scale = 1.00;
        const player = document.getElementById('player');
        const output = document.getElementById('output');
        var canvas = document.createElement("canvas");
        canvas.width = player.videoWidth * scale;
        canvas.height = player.videoHeight * scale;
        var img = document.createElement("img");

        canvas.getContext('2d').drawImage(player, 0, 0, canvas.width, canvas.height);
        img.src = canvas.toDataURL('image/jpeg', 1.0);

        let dataURL = img.src //value I want to send 
        let username = $('#username').val()

        $.ajax({
            url: '/login',
            type: 'POST',
            data: {
                imgBase64: dataURL,
                username: username
            },
            success: function(response) {
                console.log('success');
            },
            error: function(response) {
                window.location.reload()
            }
        }).done(function(data) {
            console.log("Data:", data);
            window.location = data;
        });
    }

    $('#image').change(function(e) {
        var file = this.files;
        var formData = new FormData($('form')[0]);
        formData.append('file', file[0]);
        if (this.files.length > 0) {
            $.ajax({
                url: '/displayImage',
                type: 'POST',
                data: formData,
                contentType: false,
                cache: false,
                processData: false,
                async: false,
                success: function(data) {
                    console.log(data)
                    $('.container-fluid').find('.row.justify-content-between .uploadedImage').last().remove()
                    $('.container-fluid').find('.row.justify-content-between').first().append('<div class="col-xs-12 col-sm-8 col-md-4 col-sm-offset-2 col-md-offset-4 align-self-end uploadedImage"><br><img src = "' + data.uploaded_image + '" alt="Uploaded Image" width="400px" height="400px"></div>');
                },
                error: function(data) {
                    //debugger;
                    console.log(data.responseJSON)
                    if ($('hr + ul').length == 0)
                        $('hr').after('<ul class="list-group"><li class="list-group-item d-flex justify-content-between align-items-center">' + data.responseJSON.error_msg + '<span class="badge badge-primary badge-pill">1</span></li></ul>')
                    else {
                        let value = $('hr + ul .badge').text();
                        value = parseInt(value) + 1;
                        $('hr + ul .badge').text(value);
                        $('#image').val('')
                    }
                },
            });
        }
    });

    $(document).on('hidden.bs.modal', '#cameraModal', function() {
        const player = document.getElementById('player');
        player.srcObject.getVideoTracks().forEach(track => track.stop());
        $('body').find('.modal').remove()
    });

})(jQuery);