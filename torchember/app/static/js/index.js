$(document).ready(function () {

    env = new nunjucks.Environment(new nunjucks.WebLoader(''),{ autoescape: false });

    $('.tab-btn a').click(function (e) {
        e.preventDefault()
        $(this).tab('show')
      })
    
    assign_history_menu()
    $("#first_hist_option").click()

    arm_paint()
})