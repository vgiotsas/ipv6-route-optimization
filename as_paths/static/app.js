$(document).ready(function() {

    function get_data(prefix, type='ipv4-prefix') {
        $.ajax({
            url: 'https://stat.ripe.net/data/looking-glass/data.json?resource=' + prefix,
            dataType: 'json',
            cache: false
        }).done(function(json) {
            if (type=='ipv6-prefix') {
                console.log(json);
            } else {
                console.log(json);
            }
        });
    }

    $('#form-prefixes button[type="submit"]').on('click', function(e) {
        e.preventDefault();

        // Get IPv4 data
        var ipv4_prefix = $('#ipv4-prefix').val();
        get_data(ipv4_prefix, type='ipv4-prefix');

        // // Get IPv6 data
        var ipv6_prefix = $('#ipv6-prefix').val();
        get_data(ipv4_prefix, type='ipv6-prefix');
    });

});
