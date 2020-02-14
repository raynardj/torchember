function assign_history_menu() {
    $(".history_select").click(function () {
        var hist_name = $(this).data("name")
        $("#selected").html(hist_name)
        var structure_obj = read_hist_data(hist_name)
        
        $("#model_structure").html(deploy_structure(structure_obj))
    })
}

function read_hist_data(hist_name)
{
    var aj= $.ajax({
        url:"/eread/structure/",
        async:false,
        data:JSON.stringify({name:hist_name}),
        method:"POST",
        contentType: 'application/json;charset=UTF-8'
    })
    return aj.responseJSON.data
}

function bs3_clp_panel(data)
{
    /*
    data (a JS object)
        title
        content
        id
        flavor(optional)
    */
    return env.render('static/templates/clp_panel.html',data)
}

function id_proof(str)
{
    return str.replace(/\(/g,"_").replace(/\)/g,"_").replace(/\./g,"_")
}

function deploy_structure(structure)
{
    var id = id_proof(structure.name)+"__panel";
    var content = "<div id='stats_"+id+"'> <h5>"+structure.name+"</h5> A PyTorch module tracked by torchember</div>"
    if(structure.children!=null)
    {
        for(var i=0;i<structure.children.length;i++)
        {
            var child = structure.children[i]
            content = content+deploy_structure(child)
        }
    }
    var data = {title:structure.short,id:id,content:content}
    return bs3_clp_panel(data)
}