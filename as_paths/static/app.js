$(document).ready(function() {

    google.charts.load('current', {packages: ['corechart', 'bar']});

    function toFixedRobust(number, precision) {
        if (number) {
            return number.toFixed(precision);
        }
    }

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

    /* Extract the target ASN of the given set of AS paths */
    function get_target_asn(ris_data) {
        return _.values(ris_data.data.rrcs)[0].entries[0].originating_as;
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
        /* Filter out ASNs that have very few AS paths. */
        var filtered_asn = _.filter(all_asn, function(asn) {
            if (!(asn in v4)) {
                return (v6[asn].count_v6 >= 3);
            } else if (!(asn in v6)) {
                return (v4[asn].count_v4 >= 3);
            } else {
                return (v4[asn].count_v4 >= 3) || (v6[asn].count_v6 >= 3);
            }
        });
        var filtered_asn_object = _.object(filtered_asn, filtered_asn);
        return _.mapObject(filtered_asn_object, function(asn) {
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

    function draw_charts(target_asn, raw_data) {
        var data = google.visualization.arrayToDataTable(raw_data);

        var height = raw_data.length * 60;

        var options = {
            title: 'Comparison of AS-path length towards AS ' + target_asn + ', for each of its transit providers (neighbouring AS)',
            chartArea: {width: '70%', height: '70%'},
            height: height,
            colors: ['#b0120a', '#ffab91'],
            hAxis: {
                title: 'Average AS-path length (smaller is better)',
                minValue: 0
            },
            vAxis: {
                title: 'Neighbouring AS'
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
        }).done(function(json_v6) {
            var ipv6_as_paths = [];
            var ipv4_as_paths = [];

            $.each(json_v6.data.rrcs, function(k, rrc) {
                $.each(rrc.entries, function(k, entries) {
                    ipv6_as_paths.push(entries.as_path);
                });
            });
            $.ajax({
                url: 'https://stat.ripe.net/data/looking-glass/data.json?resource=' + ipv4_prefix,
                dataType: 'json',
                cache: false
            }).done(function(json_v4) {
                $.each(json_v4.data.rrcs, function(k, rrc) {
                    $.each(rrc.entries, function(k, entries) {
                        ipv4_as_paths.push(entries.as_path);
                    });
                });
                var target_asn = get_target_asn(json_v4);
                var as_obj_unsorted = _.pairs(merge_statistics(compute_statistics(ipv4_as_paths), compute_statistics(ipv6_as_paths)));
                var as_list = _.sortBy(as_obj_unsorted, function(x) {
                    if (!("count_v4" in x[1]))
                        return x[1].count_v6;
                    else if (!("count_v6" in x[1]))
                        return x[1].count_v4;
                    else
                        return x[1].count_v4 + x[1].count_v6;
                }).reverse();
                var data = []
                data.push(['AS', 'IPv4', {type: 'string', role: 'tooltip'}, 'IPv6', {type: 'string', role: 'tooltip'}]);
                _.map(as_list, function(x) {
                    k = x[0];
                    v = x[1];
                    data.push([k, v.average_length_v4, 'Average AS-path length over ' + v.count_v4 + ' AS paths: ' + toFixedRobust(v.average_length_v4, 2),
                               v.average_length_v6, 'Average AS-path length over ' + v.count_v6 + ' AS paths: ' + toFixedRobust(v.average_length_v6, 2)]);
                });
                draw_charts(target_asn, data);
            });
        });
    }

    function show_adjacency_score(asn) {
        $.ajax({
            url: '/data/ladjscore.20170701.json',
            dataType: 'json',
            cache: true
        }).done(function(json) {
            $('#adjacency-asn').text(asn);
            if (asn in json) {
                $('#alert-adjacency').hide();
                var scores = json[asn];
                var text = '';
                text += '<strong>' + scores.adj_v4 + '</strong> IPv4 peers<br />';
                text += '<strong>' + scores.adj_v6 + '</strong> IPv6 peers<br />';
                text += '<strong>' + scores.adj_v4andv6 + '</strong> simultaneous IPv4 + IPv6 peers<br />';
                text += 'Adjacency score: <strong>' + scores.adj_score.toFixed(2) + '</strong>';
                $('#adjacency-scores').html(text);
            } else {
                $('#alert-adjacency').show();
                $('#alert-adjacency').text('AS ' + asn + ' not found in RIS data, sorry.');
            }
        });
    }

    function compute_stats_from_probes(asn) {
        $.ajax({
            url: 'https://stat.ripe.net/data/atlas-probes/data.json?resource=' + asn,
            dataType: 'json',
            cache: false
        }).done(function(json) {
            $('#alert-probe').hide();
            var probe = pick_probe(json);
            if (!probe) {
                $('#alert-probe').show();
                $('#alert-probe').text('No Atlas probe found in this ASN, sorry')
                return;
            }
            get_data(probe.prefix_v4, probe.prefix_v6);
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
        $('#alert-probe').hide();
        compute_stats_from_probes(asn);
        show_adjacency_score(asn);
    });

    var $loading = $('#loading').hide();
    $(document).ajaxStart(function () {
        $('#chart').text('');
        $loading.show();
    }).ajaxStop(function () {
        $loading.hide();
    });
});
