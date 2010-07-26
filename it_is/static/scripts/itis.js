$.featureSupport({
    cssClasses: false,
    jsObject: true
});


// Returns the URL to the API with the passed type and query.
var api_path = function(type, query){
    return {
        'all': '/api/statements/',
        'random': '/api/statements/' + encodeURI(query) + '/',
        'search': '/api/statements/search/' + encodeURI(query) + '/',
        'tags': '/api/tags/',
        'popular_tags': '/api/tags/popular/',
        'by_tag': '/api/tags/search/' + encodeURI(query) + '/',
        'count': '/api/statements/count/',
    }[type]
}


var hash = function(){
    if(window.location.hash)
        return window.location.hash.replace(/^#/, '');
    return false;
}


var List = Class.create({
    perpage: 5,
    initialize: function(){
        this.statements = []
        this.currentPage = 1;
        
        $('.statement-list').remove();
        this.populate(hash());
    },
    
    
    // Adds the passed object to the list
    add: function(obj){
        this.statements.push(obj)
    },
    
    
    // Returns the object of the passed UID
    get: function(id){
        for(var i=0; i < this.statements.length; i++){
            if(this.statements[i].sid == id)return this.statements[i]
        }
        return false;
    },
    
    
    // Removes the member of the passed UID from the list
    remove: function(id){
        for(var i=0; i < this.statements.length; i++){
            if(this.statements[i].sid == id){
                this.statements.splice(i, 1);
            }
        }
    },
    
    
    // Render a single list
    render: function(page){
        
        var list = $('<ul/>', {
                'class': 'statement-list'
            }),
            p = (page === undefined) ? this.currentPage : page,
            statements = this.page(p),
            randomBetween = function(min, max){
                return Math.round(min + (Math.random() * (max - min)));
            },
            sizes = ['large', 'large', 'medium', 'medium', 'medium', 'small', 'small'];
        
        // Calculate random x-axis positions
        var widthCoefficient = ($('#pagebody').width() - 475) / this.perpage;
        var lefts = [
            randomBetween(0, 10),
            widthCoefficient * 4 - randomBetween(0, 10),
        ];
        for(var i = 1; i <= this.perpage - 2; i++)
            lefts.push(randomBetween(-15, 15) + widthCoefficient * i);
        
        // Calculate random y-axis positions
        var heightCoefficient = ($('#pagebody').height() - 140) / this.perpage;
        var tops = [
            randomBetween(0, 10),
            heightCoefficient * 4 - randomBetween(0, 10),
        ];
        for(var i = 1; i <= this.perpage - 2; i++)
            tops.push(randomBetween(-15, 15) + heightCoefficient * i);
        
        for(var i=0; i < statements.length; i++){
            
            // Calculate random size and position
            var randomSize = sizes.splice(Math.floor(Math.random() * sizes.length), 1)[0];
            var randomTop = tops.splice(Math.floor(Math.random() * tops.length), 1)[0] + 25;
            var randomLeft = lefts.splice(Math.floor(Math.random() * lefts.length), 1)[0] + 75;
            
            // Insert into list
            statements[i].render().addClass(randomSize).css({
                'left': randomLeft,
                'top': randomTop
            }).appendTo(list);
            
        }
        
        return list;
        
    },
    
    
    // Populates the list with statements tagged with the passed query (or all),
    // if nothing is passed.
    populate: function(query){
        this.statements = [];
        var self = this;
        $.ajax({
            'dataType': 'json',
            'url': (query) ? api_path('search', query) : api_path('all'),
            'success': function(data, textStatus, XMLHttpRequest){
                for(var i = 0; i < data.length; i++){
                    var statement = data[i];
                    self.add(new Statement(
                        statement['id'],
                        statement['tag'][0],
                        statement['statement'],
                        statement['tag'][2]
                    ));
                }
                self.render(1).appendTo('#pagebody');
                $('body > header > h1 > strong').text((query) ? query : 'Everything');
                draggable.refresh();
            }
        });
    },
    
    
    // Return a slice of the 
    page: function(n){
        var end = n * this.perpage;
        var start = end - this.perpage;
        return this.statements.slice(start, end)
    },
    
    
    isFirstPage: function(){
        return (this.currentPage == 1);
    },
    
    
    isLastPage: function(){
        return (this.currentPage == Math.ceil(list.statements.length / list.perpage));
    },
    
    
    // Moves list to the next page
    nextPage: function(){
        
        if(!this.isLastPage()){
            
            // Send out current list
            $('.statement-list').animate({
                left: '-=600px',
                opacity: 0
            }, 200, function(){
                $(this).remove();
            });
            
            // Bring in next list
            var newList = this.render(this.currentPage+1).css({
                opacity: 0,
                left: 600
            }).appendTo('#pagebody').animate({
                left: '-=600px',
                opacity: 1
            }, 200);
            
            draggable.init();
            this.currentPage++;
            
        }
        
    },
    
    
    // Moves list to the previous page
    prevPage: function(){
        
        if(!this.isFirstPage()){
            
            // Send out current list
            $('.statement-list').animate({
                left: '+=600px',
                opacity: 0
            }, 200, function(){
                $(this).remove();
            });
            
            // Bring in next list
            var newList = this.render(this.currentPage-1).css({
                opacity: 0,
                left: -600
            }).appendTo('#pagebody').animate({
                left: '+=600px',
                opacity: 1
            }, 200);
            
            draggable.init();
            this.currentPage--;
            
        }
        
    }
});


var Collection = Class.create(List, {
    initialize: function(){
        this.statements = []
    },
    add: function($super, obj){
        if(!this.get(obj.sid)){
            $super(obj);
            this.updateCookie();
            this.updateCount();
        }
    },
    remove: function($super, obj){
        $super(obj);
        this.updateCookie();
        this.updateCount();
    },
    updateCookie: function(){
        var cookieValue = '';
        for(var i=0; i < this.statements.length; i++){
            cookieValue += new String(this.statements[i].sid);
            if((i+1) != this.statements.length) cookieValue += ',';
        }
        $.cookie('itis_collection', cookieValue);
    },
    updateCount: function(){
        $('#collection header h2').text(this.statements.length)
    }
});
var myStatements = new Collection;


/**/
var Statement = Class.create({
    sizes: ['small', 'medium', 'large'],
    initialize: function(sid, tag, statement, color){
        this.sid = sid;
        this.tag = tag;
        this.statement = statement;
        this.color = color;
    },
    
    links: {
        'add': '<a class="add-collection collection-link" href="">Add to Collection</a>',
        'remove': '<a class="remove-collection collection-link" href="">Remove from Collection</a>'
    },
    
    template: function(){
        var ret = '<h2>%(statement)s</h2>';
        ret += '<div class="tag" style="background-color: #%(color)s">%(tag)s</div>';
        ret += (!!collection.get(this.sid)) ? this.links.remove : this.links.add;
        return ret;
    },
    render: function(){
        var item = $('<li/>', {
            html: this.template().interpolate({
                statement: this.statement.replace(/(it is)/gi, '<strong>$1</strong>').replace(/(it's)/gi, '<strong>$1</strong>'),
                tag: this.tag,
                color: this.color
            }),
            'class': 'statement',
            id: 'statement-' + this.sid,
            draggable: 'true'
        });
        item.find('.tag').data('tag', this.tag);
        return item.data('statement', this);
    },
    addToCollection: function(){
        collection.add(this);
        $('#statement-' + this.sid).append(this.links.remove).find('.add-collection').remove();
    },
    removeFromCollection: function(){
        collection.remove(this.sid);
        $('#statement-' + this.sid).append(this.links.add).find('.remove-collection').remove();
    },
    
});


var overlay = {
    overlay: $('<div/>', {
        id: 'overlay'
    }),
    'show': function(){
        this.overlay.appendTo('body').fadeIn(150);
    },
    'hide': function(){
        $('#overlay').fadeOut(150);
    }
};


$(document).ready(function(){
    
    /*  */
    var adjustWindowSize = function(){
        var w = $(window),
            p = $('#pagebody');
        p.css('height', (w.height() - parseInt(p.css('top'))));
    }
    adjustWindowSize();
    $(window).scroll(adjustWindowSize).resize(adjustWindowSize);
    
    
    draggable = {
        refresh: function(){
            if(this.draggers){
                this.draggers.each(function(index, element){
                    $(this).unbind('draggable');
                });
            }
            this.init();
        },
        init: function(){
            
            var cancel = function(evt){
                evt.preventDefault();
                return false;
            };
            
            $('.statement')
                .bind('dragstart', function(evt){
                    overlay.show();
                    $('#collection').addClass('dragging').animate({
                            'height': 20
                        }, 125);
                    var dragProxy = $(this).clone().attr('id', null).addClass('dragging').appendTo('body');
                    return dragProxy;
                })
                .bind('drag', function(evt){
                    $( evt.dragProxy ).css({
                        left: evt.offsetX,
                        top: evt.offsetY,
                        zIndex: 10000
                    });
                })
                .bind('dragend', function(evt){
                    overlay.hide();
                    $('#collection').removeClass('dragging').stop().animate({
                            'height': 10
                        }, 125);
                    $( evt.dragProxy ).fadeOut( "normal", function(){
                        $( this ).remove();
                    });
                });
            
            $('#collection h1')
                .bind('dropstart', function(evt){
                    $(this).addClass('hover');
                })
                .bind('drop', function(evt){
                    $(evt.dragTarget).data('statement').addToCollection();
                })
                .bind('dropend', function(evt){
                    $(this).removeClass('hover');
                });            
            
        }
    };
    
    
    list = new List;
    collection = new Collection;
    
    
    // Tag display
    $('.tag').live('click', function(evt){
        evt.preventDefault();
        var tag = $(this).data('tag');
        window.location.hash = tag;
        list = new List;
    });
    
    
    // Events for next/previous buttons
    $('<a/>', {
        'href': '#',
        'id': 'prev',
        'text': 'Previous',
        'click': function(evt){
            evt.preventDefault();
            list.prevPage();
        }
    }).appendTo('#pagebody');
    $('<a/>', {
        'href': '#',
        'id': 'next',
        'text': 'Next',
        'click': function(evt){
            evt.preventDefault();
            list.nextPage();
        }
    }).appendTo('#pagebody');
    
    
    // Add/remove from collection links on individual statements
    $('.add-collection, .remove-collection').live('click', function(evt){
        evt.preventDefault();
        var statement = $(this).closest('.statement').data('statement');
        if($(this).hasClass('add-collection')){
            statement.addToCollection();
        }else{
            statement.removeFromCollection();
        }
    });
    
    
    // Show and hide "My Collection" panel
    $('#collection > header > h1').toggle(function(evt){
        evt.preventDefault();
        overlay.show();
        $(this).closest('#collection').animate({
            'height': $(window).height() - 75
        }, 400);
    }, function(evt){
        evt.preventDefault();
        overlay.hide();
        $(this).closest('#collection').animate({
            'height': 10
        }, 275);
    });
    
});