$(document).ready(function() {

    google.charts.load('current', {packages: ['corechart', 'bar']});

    function average_length(as_paths) {
        var sum = 0
        for( var i = 0; i < as_paths.length; i++ ){
            sum += as_paths[i].length;
        }
        var avg = sum / as_paths.length;
        return avg;
    }

    function compute_statistics(as_paths) {
        var cleaned_as_paths = _.map(as_paths, function(as_path) { return _.uniq(as_path.split(' ')) });
        var groups = _.groupBy(cleaned_as_paths, function(as_path) { return as_path[as_path.length - 2] });
        var groups_stats = _.mapObject(groups, function(as_paths) { return {count: as_paths.length, average_length: average_length(as_paths)} });
        /* { neighbour_AS: {count: <number of AS paths through this neighbour,
                            average_length: <average length of AS paths through this neighbour>}
           }
        */
        return groups_stats;
    }

    /* Given JSON data from the RIPE API with a list of probes, only keep
     * probes that have the same IPv4 and IPv6 ASN, and try to pick a
     * connected probe (by taking the most recently connected one) */
    function pick_probe(probes_json) {
        var probes = probes_json.data.probes;
        probes = _.filter(probes, function(probe) { return probe.asn_v4 == probe.asn_v6 });
        if (probes.length == 0) {
            return;
        } else {
            return _.max(probes, function(probe) { return probe.last_connected });
        }
    }

    /* Given per-neighbouring-AS statistics for IPv4 and IPv6, returns
     * combined statistics. */
    function merge_statistics(v4_stats, v6_stats) {
        var v4 = _.mapObject(v4_stats, function(stats, asn) {
            return { count_v4: stats.count,
                     average_length_v4: stats.average_length };
        });
        var v6 = _.mapObject(v6_stats, function(stats, asn) {
            return { count_v6: stats.count,
                     average_length_v6: stats.average_length };
        });
        var all_asn = _.uniq(_.flatten([_.keys(v4), _.keys(v6)]));
        var all_asn_object = _.object(all_asn, all_asn);
        console.log(all_asn);
        return _.mapObject(all_asn_object, function(asn) {
            /* Handle ASN that only appears in either v4 or v6 */
            if (!(asn in v4)) {
                return v6[asn];
            } else if (!(asn in v6)) {
                return v4[asn];
            } else {
                return _.extend({}, v4[asn], v6[asn]);
            }
        });
    }

    function draw_charts(as) {
        var data = google.visualization.arrayToDataTable(as);

        var options = {
            title: 'AS Paths',
            chartArea: {width: '80%'},
            colors: ['#b0120a', '#ffab91'],
            hAxis: {
                title: 'Average Lengths',
                minValue: 0
            },
            vAxis: {
                title: 'AS'
            }
        };
        var chart = new google.visualization.BarChart(document.getElementById('chart'));
        chart.draw(data, options);
    }

    function get_data(ipv6_prefix, ipv4_prefix) {
        $.ajax({
            url: 'https://stat.ripe.net/data/looking-glass/data.json?resource=' + ipv6_prefix,
            dataType: 'json',
            cache: false
        }).done(function(json) {
            var ipv6_as_paths = [];
            var ipv4_as_paths = [];

            $.each(json.data.rrcs, function(k, rrc) {
                $.each(rrc.entries, function(k, entries) {
                    ipv6_as_paths.push(entries.as_path);
                });
            });
            $.ajax({
                url: 'https://stat.ripe.net/data/looking-glass/data.json?resource=' + ipv4_prefix,
                dataType: 'json',
                cache: false
            }).done(function(json) {
                $.each(json.data.rrcs, function(k, rrc) {
                    $.each(rrc.entries, function(k, entries) {
                        ipv4_as_paths.push(entries.as_path);
                    });
                });
                var as_obj = merge_statistics(compute_statistics(ipv4_as_paths), compute_statistics(ipv6_as_paths));
                var data = []
                data.push(['AS', 'IPv4', 'IPv6']);
                $.each(as_obj, function(k, v) {
                    data.push([k, v.average_length_v4, v.average_length_v6]);
                });
                draw_charts(data);
            });
        });
    }

    function compute_stats_from_probes(asn) {
        $.ajax({
            url: 'https://stat.ripe.net/data/atlas-probes/data.json?resource=' + asn,
            dataType: 'json',
            cache: false
        }).done(function(json) {
            var probe = pick_probe(json);
            if (!probe) {
                alert("No Atlas probe found in this ASN, sorry");
                return;
            }
            console.log(probe);
            // Do something with probe.prefix_v4 and probe.prefix_v6
        });
    }

    $('#form-prefixes button[type="submit"]').on('click', function(e) {
        e.preventDefault();

        // Get IP data
        var ipv6_prefix = $('#ipv6-prefix').val();
        var ipv4_prefix = $('#ipv4-prefix').val();
        get_data(ipv6_prefix, ipv4_prefix);
    });

    $('#form-asn button[type="submit"]').on('click', function(e) {
        e.preventDefault();

        // Get ASN data
        var asn = $('#asn').val();
        compute_stats_from_probes(asn);
    });

    var $loading = $('#loading').hide();
    $(document).ajaxStart(function () {
        $loading.show();
    }).ajaxStop(function () {
        $loading.hide();
    });
});
