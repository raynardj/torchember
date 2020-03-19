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
    //console.log(log_files_dt)
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

function get_hist_name(){
    var hist_name = $("#selected").html()
    return hist_name
}

function deploy_module(structure) {
    var id = panel_id(structure.name);
    var content = ""
    if (structure.children != null) {
        for (var i = 0; i < structure.children.length; i++) {
            var child = structure.children[i]
            content = content + deploy_module(child)
        }
    }
    var data = { title: structure.short, long_name:structure.name,
        id: "log"+id, 
        content: content,
        flavor: "default" ,}
    return bs3_render("clp_panel_2.html",data)
}

function paint_split(data) {
    // data = module_strat(data)
    var result = split_count(data)
    var groupby = bs3_render("groupby_btns.html", { counters: result.tensor })
    var structure_obj = read_structure_data(get_hist_name())
    console.log(structure_obj)
    var module_ct = deploy_module(structure_obj)
    $(".groupby_kv").each(function () {
        $(this).html(groupby)
    })
    $(".module_filter").each(function () {
        $(this).html(module_ct)
    })
    arm_btn_filter()
    click_filter_first()
}

function arm_log_file_click(log_file_dom) {
    $(log_file_dom).click(function () {
        var dt = $(this).data()
        // paint_line_chart()
        open_log(dt.hist_name, dt.file_name)
        paint_split(window.log_file_now)
    })
}

function arm_btn_filter(){
    $(".btn_filter").each(function(){
        $(this).click(function(){
            
            var dt = $(this).data()
            $(".close_"+String(dt.cate)).each(function(){
                $(this).click()
            })
            $(".log_filters").append(bs3_render("log_filter_cancel_btn.html",dt))
            arm_filter_close_btn()
            log_pass_through_filter()
        })
    })
}

function click_filter_first(){
    $(".btn_filter_module:first").click()
    $(".btn_filter_ttype:first").click()
    $(".btn_filter_tname:first").click()
}

function arm_filter_close_btn(){
    $(".filter_close_btn").each(function(){
        $(this).click(function(){
            var close_id = $(this).data("close_id")
            $("."+String(close_id)).each(function(){$(this).remove()})
        })
    })
}

function read_log_filters()
{
    window.log_filters = {}
    $(".cancel_filter_btn").each(function(){
        var dt = $(this).data()
        window.log_filters[dt.cate]=dt.k
    })
    return window.log_filters
}

function log_pass_through_filter()
{
    // filter through log with filter controls
    var log = window.log_file_now
    var result_list = []

    var filters = read_log_filters()
    var fkeys = Object.keys(filters)
    for(i in log)
    {
        var row = log[i]
        row.filter_match_ = true
        for(var j=0;j<fkeys.length; j++)
        {
            k = fkeys[j]
            if(row[k]!=filters[k]) {row.filter_match_ = false;break}
        }
        if(row.filter_match_==true){
            delete row.filter_match_
            result_list.push(row)
        }
    }
    
    window.log_filtered_now = result_list
    return result_list
}
function refactor_log_charts(){
    // log_refactored
    var lrf  = {}
    var lrf_count = {}
    for(i in window.log_filtered_now)
    {
        var row = window.log_filtered_now[i]
        for(k in row)
        {
            if(lrf.hasOwnProperty(k)==false)
            {lrf[k] = []}
            lrf[k].push(row[k])
        }
    }
    for(k in lrf)
    {
        lrf_count[k] = lrf[k].length
    }
    // todo: build charts upon here
    window.log_refactored = lrf
    window.log_refactored_count = lrf_count
}

function paint_line_chart(conf) {
    /*
    var conf = {
        frameId:"xxx",
        titleText:"xxx",
        seriesName:"xx",
        data:array of float,
        xData: data for x-axis
    }
    */
    // console.log("Start Painting line chart")
    var myChart = echarts.init(document.getElementById(conf.frameId));

    option = {
        tooltip: {
            trigger: 'axis',
            position: function (pt) {
                return [pt[0], '10%'];
            }
        },
        title: {
            left: 'center',
            text: conf.titleText,
        },
        toolbox: {
            feature: {
                dataZoom: {
                    yAxisIndex: 'none'
                },
                restore: {},
                saveAsImage: {}
            }
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: conf.xData
        },
        yAxis: {
            type: 'value',
            boundaryGap: [0, '100%']
        },
        dataZoom: [{
            type: 'inside',
            start: 0,
            end: 10
        }, {
            start: 0,
            end: 10,
            handleIcon: 'M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7V23h6.6V24.4z M13.3,19.6H6.7v-1.4h6.6V19.6z',
            handleSize: '80%',
            handleStyle: {
                color: '#fff',
                shadowBlur: 3,
                shadowColor: 'rgba(0, 0, 0, 0.6)',
                shadowOffsetX: 2,
                shadowOffsetY: 2
            }
        }],
        series: [
            {
                name: conf.seriesName,
                type: 'line',
                smooth: true,
                symbol: 'none',
                sampling: 'average',
                itemStyle: {
                    color: 'rgb(255, 70, 131)'
                },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
                        offset: 0,
                        color: 'rgb(255, 158, 68)'
                    }, {
                        offset: 1,
                        color: 'rgb(255, 70, 131)'
                    }])
                },
                data: conf.data
            }
        ]
    };
    console.log(option)
    myChart.setOption(option);
}

function paint_log_charts(){
    refactor_log_charts()
    var lrf = window.log_refactored
    var lrf_ct = window.log_refactored_count
    $("#log_line_charts").html("")
    for(dim in lrf)
    {
        if(lrf_ct[dim]<2)
        {
            continue
        }
        if(typeof(lrf[dim][0])!="number")
        {
            continue 
            console.log("not a column of number")
            // todo: non-number data using other ways of visualization
        }

        var dt = lrf[dim]
        paint_log_chart(dt,dim,"log_line_charts")
    }
}

function paint_log_chart(dt,dim,parent_id)
{
    var frame_id = "chart_frame_"+String(dim)
    var frame = bs3_render("chart_frame.html", {dim:dim,frame_id:frame_id,width:600,height:400})
    $("#"+String(parent_id)).append(frame)
    var conf = {
        frameId:frame_id,
        titleText:String(dim),
        seriesName:"Value",
        data:dt,
        xData: range(dt.length)
    }
    paint_line_chart(conf)
}

function range(n)
{
    var rt = [];
    for(var i=0; i<n; i++){rt.push(i)}
    return rt
}

function arm_paint(){
    $(".start_paint_log").each(function(){
        $(this).click(function(){
            paint_log_charts()
        })
    })
}