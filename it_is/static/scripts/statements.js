var StatementManager = (function(count){
    if (arguments.length === 2) {
        var tag = arguments[1];
    } else { tag = null; }
    var canvas = $("#statements");
    var max_statements = 0;
    var possible_pages = 0;
    var offset = 0;
    var get_statements_link = "api/statements/";
    var pages = []
    return {
        'init': function() {
            this.get_statement_count();
            this.get_statements();
        },
        'get_statement_count': function() {
            var data = (tag) ? {'tag': tag} : {};
            $.get("api/statements/count/", data, this.get_statement_count_callback)
        },
        'get_statement_count_callback': function (data, textStatus, requestObj) {
            max_statements = Number(data);
            possible_pages = Math.floor(max_statements/count);
        },
        'get_statements': function() {
            var url = get_statements_link + count + "/";
            var data = {'offset': offset};
            if (tag) {
                data['tag'] = tag;
            }
            $.get(url, data, this.get_statements_callback);
        },
        'get_statements_callback': function(data, textStatus, requestObj) {
            pages.push(data);
            offset += count;
            var data_length = data.length;
            for (var i = 0; i < data_length; i++) {
                var statement = data[i];
                var statement_markup = '<div class="statement" id="' + statement.id + '">';
                statement_markup += '<div class="tag">' + statement.tag[1] + '</div>';
                statement_markup += '<div>' + statement.statement + '</div></div>';
                var tag = $(statement_markup);
                canvas.append(tag);
            }
        },
        '_get': function(variable) {
            eval("variable = " + variable);
            return variable;
        } 
    }
 });

/* Example usage: 
    // Paginate at 5 statements:
    statement = StatementManager(5);
    statement.init();
    // Filter by tag:
    statement = StatementManager(5, "mytag");
    statement.init();
*/