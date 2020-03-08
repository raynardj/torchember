function load_log_files(hist_name) {
    var aj = $.ajax({
        url: "/eread/log_files_api/",
        async: false,
        data: JSON.stringify({ dir_name: hist_name }),
        contentType: "application/json",
        method: "POST",
    })
    return aj.responseJSON
}
function update_log_files(hist_name) {
    var log_files_dt = load_log_files(hist_name)
    console.log(log_files_dt)
    if (log_files_dt.success == false) {
        console.log(log_files_dt.data)
    }
    else {
        $(".log_files_list").each(function () {
            $(this).html(bs3_render("log_files.html", { log_files: log_files_dt.data, hist_name: hist_name }))
            $(".log_file_option").each(function () {
                arm_log_file_click(this)

            })
        })
    }
}

function open_log(hist_name, file_name) {
    var file_url = "/eread/log_file/" + String(hist_name) + "/" + file_name + "/";
    var data = $.ajax({
        url: file_url, async: false, method: "POST", success: function (dt) {
            var dt = eval(dt)
            window.log_file_now = dt
            return dt
        }
    })
    return data
}

function k_counter(result_obj, k) {
    if (result_obj.hasOwnProperty(k)) { result_obj[k] += 1 }
    else { result_obj[k] = 0 }
}
function filter_kv(data, k, v) {
    var result = []
    for (row in data) {
        if (row[k] == v) { result.push(row) }
    }
    return result
}
function module_strat(data) {
    var deepest = 0
    for (row in data) {
        row.module_list = row.module.split(".")
        row.module_len = row.module_list.length
        row.module_parent = row.module_list.split(-1).join(".")
    }
    return data
}
function split_count(data) {
    if (data) {
        var result = {}
        var module_result = {}
        result.ttype = {}
        result.tname = {}
        var data = data;
        for (i in data) {
            var row = data[i]
            k_counter(result.ttype, row.ttype)
            k_counter(module_result, row.module)
            k_counter(result.tname, row.tname)
        }
        return {tensor:result, module:module_result}
    }
    else {
        return null
    }
}

function paint_split(data) {
    // data = module_strat(data)
    var result = split_count(data)
    var groupby = bs3_render("groupby_btns.html", { counters: result.tensor })
    var module_ct = bs3_render("module_ct.html", { modules: result.module })
    $(".groupby_kv").each(function () {
        $(this).html(groupby)
    })
    $(".module_filter").each(function () {
        $(this).html(module_ct)
    })
}

function arm_log_file_click(log_file_dom) {
    $(log_file_dom).click(function () {
        var dt = $(this).data()
        // paint_line_chart()
        open_log(dt.hist_name, dt.file_name)
        paint_split(window.log_file_now)
    })
}