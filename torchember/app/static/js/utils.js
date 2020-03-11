/* Paint Functions */

function create_norm_func(mu, sigma) {
    /*
    create normal distribution function
    from mean and std
    mu, mean
    sigma, std
    */
    if (sigma == 0) {
        return false
    }
    function norm_func(x) {
        return (1 / (sigma * Math.sqrt(2 * Math.PI))) *
            Math.pow(Math.E,
                -0.5 *
                (Math.pow((x - mu), 2) / sigma)
            )
    }
    return norm_func
}

function getRandomColor() {
    var letters = '0123456789ABCDEF';
    var color = '#';
    for (var i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

function calc_bar_norm_dist(module) {
    var color = Chart.helpers.color;
    module.barChartData = { labels: [], datasets: [] }
    for (var i = 0; i < module.data.length; i++) {
        var row = module.data[i]
        var color_ = getRandomColor()
        row.norm_func = create_norm_func(row.mean, row.std);
        if (row.norm_func != false) {
            module.barChartData.datasets.push({
                label: row.tname,
                boardWidth: 0.2,
                data: [],
                backgroundColor: color(color_).alpha(0.5).rgbString(),
                borderColor: color_,
                row_norm_func: row.norm_func
            })
        }
    }
    for (var i = 0; i < 31; i++) {
        var x = -3. + i * 0.2
        module.barChartData.labels.push(x.toFixed(2))
        for (var j = 0; j < module.barChartData.datasets.length; j++) {
            module.barChartData.datasets[j].data[i] = module.barChartData.datasets[j].row_norm_func(x);
        }
    }
}

function paint_bar(module) {
    var canvas = document.getElementById("canvas_norm_dist_" + String(module.idx))
    window.myBar = new Chart(canvas, {
        type: 'bar',
        data: module.barChartData,
        options: {
            responsive: true,
            legend: {
                position: 'top',
            }
        }
    });
}

function paint_module_recon_norm(module) {
    var p_id = panel_id(module.module);
    var stats_id = "stats_" + p_id;
    calc_bar_norm_dist(module)
    $("#" + stats_id).html(bs3_norm_module(module))
    paint_bar(module)
}

function paint_standard_module(module, cols) {
    var p_id = panel_id(module.module);
    var stats_id = "stats_" + p_id;
    $("#" + stats_id).html(bs3_standard_module(module, cols))
}

function build_by_module(latest) {
    var by_module = {}
    for (var i = 0; i < latest.length; i++) {
        var record = latest[i]
        for (var k in record) {
            if (typeof record[k] == "number") {
                record[k] = record[k].toFixed(5)
            }
        }
        if (by_module[record.module] == null) { by_module[record.module] = { module: record.module, data: [], idx: i } }

        by_module[record.module].data.push(record)
    }
    return by_module
}

function paint_recon_norm(latest) {
    /*
    latest: json, orient='record'
    vis: json, visualization data
    */
    var by_module = build_by_module(latest)
    for (mname in by_module) {
        paint_module_recon_norm(by_module[mname])
    }
}

function paint_dict2table(latest, cols, vis) {
    var by_module = build_by_module(latest);
    for (mname in by_module) {
        paint_standard_module(by_module[mname], cols)
    }
}

/* A Map of Paint Functions */
vis_map = {
    standard: paint_standard,
    dict_to_table: paint_dict2table
}

function paint_standard(latest, cols, vis) {
    // over write cols in this function
    cols = ["ttype", "tname", "shape", "cnt_zero", "mean", "std", "min", "max"]
    var by_module = build_by_module(latest);
    for (mname in by_module) {
        paint_standard_module(by_module[mname], cols)
    }
}


function assign_history_menu() {
    $(".history_select").click(function () {
        var hist_name = $(this).data("name")
        $("#selected").html(hist_name)
        var structure_obj = read_structure_data(hist_name)

        $("#model_structure").html(deploy_structure(structure_obj))
        update_log_files(hist_name)
        // assign the refresh-btn
        $("#table-stats-btn").click(function () { update_latest(hist_name) })
        $("#reconstruct-gaussian-btn").click(function () { update_reconstruct_norm(hist_name) })
        $("#table-stats-raw-btn").click(function () { update_latest_raw(hist_name) })
        $(".btn_update_log_files").each(function () {
            $(this).click(function () {
                update_log_files(hist_name)
            })
        })
    })
}

function read_structure_data(hist_name) {
    var aj = $.ajax({
        url: "/eread/structure/",
        async: false,
        data: JSON.stringify({ name: hist_name }),
        method: "POST",
        contentType: 'application/json;charset=UTF-8'
    })
    return aj.responseJSON.data
}

function read_latest_data(hist_name) {
    /*
    Read the lateset stats update from the lastest api
    hist_name: history name
     */
    var aj = $.ajax({
        url: "/eread/latest/",
        async: false,
        data: JSON.stringify({ name: hist_name }),
        method: "POST",
        contentType: 'application/json;charset=UTF-8'
    })
    return aj.responseJSON.data
}

function bs3_render(template, data) {
    return env.render('static/templates/' + String(template), data)
}

function bs3_clp_panel(data) {
    /*
    data (a JS object)
        title
        content
        id
        flavor(optional)
    */
    return bs3_render('clp_panel.html', data)
}

function bs3_standard_module(module, cols) {
    module.cols = cols
    return env.render('static/templates/standard_module.html', module)
}

function bs3_norm_module(module) {
    return env.render('static/templates/norm_module.html', module)
}

function id_proof(module_name) {
    return module_name.replace(/\(/g, "_").replace(/\)/g, "_").replace(/\./g, "_")
}
function panel_id(module_name) {
    return id_proof(module_name) + "__panel"
}

function deploy_structure(structure) {
    var id = panel_id(structure.name);
    var content = "<div id='stats_" + id + "'> <h5>" + structure.name + "</h5> A PyTorch module tracked by torchember</div>"
    if (structure.children != null) {
        for (var i = 0; i < structure.children.length; i++) {
            var child = structure.children[i]
            content = content + deploy_structure(child)
        }
    }
    var data = { title: structure.short, id: id, content: content, flavor: "primary" }
    return bs3_clp_panel(data)
}
function update_reconstruct_norm(hist_name) {
    var latest_data = read_latest_data(hist_name)
    var latest = latest_data.latest
    paint_recon_norm(latest);
}

function update_latest(hist_name) {
    var latest_data = read_latest_data(hist_name);
    if (latest_data.success) {
        return null
    }
    var latest = latest_data.latest;
    var vis = latest_data.vis;
    var cols = latest_data.cols;
    var paint_func = vis_map[vis["vis_type"]]
    paint_func(latest, cols, vis)
}

function update_latest_raw(hist_name) {
    var latest_data = read_latest_data(hist_name);
    var pre = document.createElement("pre")
    $(pre).append(JSON.stringify(latest_data, null, 2))
    $("#raw_data_block").html(pre)
}



