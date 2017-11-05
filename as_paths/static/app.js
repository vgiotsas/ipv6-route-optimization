$(document).ready(function() {

    average_length = function(as_paths) {
        var sum = 0
        for( var i = 0; i < as_paths.length; i++ ){
            sum += as_paths[i].length;
        }
        var avg = sum / as_paths.length;
        return avg;
    }

    compute_statistics = function(as_paths) {
        var cleaned_as_paths = _.map(as_paths, function(as_path) { return _.uniq(as_path.split(' ')) });
        var groups = _.groupBy(cleaned_as_paths, function(as_path) { return as_path[as_path.length - 2] });
        var groups_stats = _.mapObject(groups, function(as_paths) { return {count: as_paths.length, average_length: average_length(as_paths)} });
        /* { neighbour_AS: {count: <number of AS paths through this neighbour,
                            average_length: <average length of AS paths through this neighbour>}
           }
        */
        return groups_stats;
    }

    function get_data(prefix, type='ipv4-prefix') {
        $.ajax({
            url: 'https://stat.ripe.net/data/looking-glass/data.json?resource=' + prefix,
            dataType: 'json',
            cache: false
        }).done(function(json) {
            if (type=='ipv6-prefix') {
                var ipv6_as_paths = [];
                $.each(json.data.rrcs, function(k, rrc) {
                    $.each(rrc.entries, function(k, entries) {
                        ipv6_as_paths.push(entries.as_path);
                    });
                });
                var ipv6_as = compute_statistics(ipv6_as_paths);
                console.log(ipv6_as);
            } else {
                var ipv4_as_paths = [];
                $.each(json.data.rrcs, function(k, rrc) {
                    $.each(rrc.entries, function(k, entries) {
                        ipv4_as_paths.push(entries.as_path);
                    });
                });
                var ipv4_as = compute_statistics(ipv4_as_paths);
                console.log(ipv4_as);
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
