$.featureSupport({
    cssClasses: false,
    jsObject: true
});


var slugify = function(text) {
    return text.replace(/\s+/g,'-').replace(/[^a-zA-Z0-9\-]/g,'').toLowerCase();
}


// Returns the URL to the API with the passed type and query.
var api_path = function(type, query){
    return {
        'all': BASE_PATH + 'api/statements/',
        'random': BASE_PATH + 'api/statements/' + encodeURI(query) + '/',
        'search': BASE_PATH + 'api/statements/search/' + encodeURI(query) + '/',
        'list': BASE_PATH + 'api/statements/list/' + encodeURI(query),
        'tags': BASE_PATH + 'api/tags/',
        'popular_tags': BASE_PATH + 'api/tags/popular/',
        'by_tag': BASE_PATH + 'api/tags/search/' + encodeURI(query) + '/',
        'count': BASE_PATH + 'api/statements/count/',
    }[type]
}


var hash = function(){
    if(window.location.hash)
        return window.location.hash.replace(/^#/, '');
    return false;
}


var Modal = Class.create({
    initialize: function(url){
        this.url = url;
        overlay.show(false, 'showing-modal');
        $.ajax({
            'dataType': 'html',
            'url': url,
            'success': function(data, textStatus, XMLHttpRequest){
                overlay.overlay.html(data);
                $('<a/>', {
                    href: '#',
                    class: 'close',
                    click: function(evt){
                        evt.preventDefault();
                        modal.close();
                    }
                }).appendTo(overlay.overlay);
                $(window).trigger('newModal');
            }
        });
    },
    close: function(){
        overlay.overlay.children('section').animate({
            left: '-=600px',
            opacity: 0
        }, 200, function(){
            $(this).remove();
            overlay.hide();
        });
    }
});


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
    
    
    // Render a single page of the current list
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
        
        if(this.isFirstPage()){ $('#prev:visible').fadeOut(250) }else{ $('#prev:not(:visible)').fadeIn(250) }
        if(this.isLastPage()){ $('#next:visible').fadeOut(250) }else{ $('#next:not(:visible)').fadeIn(250) }
        
        
        return list;
        
    },
    
    
    // Populates the list with statements tagged with the passed query (or all),
    // if nothing is passed.
    populate: function(query){
        this.statements = [];
        var self = this;
        
        $('#pagebody .statement-list').remove();
        loader.show();
        
        var url, collection = false;
        if(query){
            url = api_path('search', query);
            if(query.match(/^[\d,]+/)){
                url = api_path('list', query)
                collection = true;
            }
        }else{
            url = api_path('all');
        };
        
        $.ajax({
            'dataType': 'json',
            'url': url,
            'success': function(data, textStatus, XMLHttpRequest){
                loader.hide();
                if(data.length){
                    for(var i = 0; i < data.length; i++){
                        var statement = data[i];
                        self.add(new Statement(
                            statement['id'],
                            statement['tag'],
                            statement['statement']
                        ));
                        if(query && i==0) var tag_display = statement['tag'][1];
                    }
                    self.render(1).appendTo('#pagebody');
                    draggable.refresh();
                }else{
                    $('#next:visible, #prev:visible').fadeOut(250);
                    $('<ul/>', {
                        id: 'empty',
                        class: 'statement-list',
                        html: '<li>There are no statements with this tag.</li>'
                    }).appendTo('#pagebody');
                }
                $('body > header > h1 > a').text((collection) ? 'A Collection' : ((tag_display) ? tag_display : 'Everything'));
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
            
            this.currentPage++;
            
            // Bring in next list
            var newList = this.render(this.currentPage).css({
                opacity: 0,
                left: 600
            }).appendTo('#pagebody').animate({
                left: '-=600px',
                opacity: 1
            }, 200);
            
            draggable.init();
            
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
            
            this.currentPage--;
            
            // Bring in next list
            var newList = this.render(this.currentPage).css({
                opacity: 0,
                left: -600
            }).appendTo('#pagebody').animate({
                left: '+=600px',
                opacity: 1
            }, 200);
            
            draggable.init();
            
        }
        
    }
    
});


var Collection = Class.create(List, {
    initialize: function(){
        this.statements = [];
        self = this;
        var c = $.cookie('itis_collection');
        if(c && c != ''){
            $.ajax({
                'dataType': 'json',
                'url': api_path('list', c),
                'success': function(data, textStatus, XMLHttpRequest){
                    for(var i = 0; i < data.length; i++){
                        var statement = data[i];
                        self.add(new Statement(
                            statement['id'],
                            statement['tag'],
                            statement['statement']
                        ));
                    }
                }
            });
        }
    },
    
    
    add: function($super, obj){
        if(!this.get(obj.sid)){
            $super(obj);
            this.update();
        }
    },
    
    
    remove: function($super, obj){
        $super(obj);
        this.update();
    },
    
    
    
    update: function(){
        this.updateCookie();
        this.updateCount();
        this.populate();
        adjustWindowSize();
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
    },
    
    populate: function($super){
        $('#collection > div').html('');
        var objs = this.render();
        for(var i = 0; i < objs.length; i++){
            $('#collection > div').append(objs[i]);
        }
    },
    
    render: function($super){
        var list = [];
        
        list.push($('<div/>', {
            'class': 'collection-url',
            'html': '<label for="collection-url">Share my collection: </label><input readonly="readonly" type="text" id="collection-url" name="collection-url" value="http://remixthought.org/it-is/#' + $.cookie('itis_collection') + '"/>'
        }));
        
        list.push($('<ul/>', {
            'class': 'collection-list'
        }));
        for(var i=0; i < this.statements.length; i++){
            this.statements[i].render().appendTo(list[1]);
        }
        
        return list;
    }
    
});


/**/
var Statement = Class.create({
    sizes: ['small', 'medium', 'large'],
    initialize: function(sid, tag, statement){
        this.sid = sid;
        this.tag_slug = tag[0];
        this.tag = tag[1];
        this.color = tag[2];
        this.statement = statement;
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
        item.find('.tag').data('tag', this.tag_slug);
        return item.data('statement', this);
    },
    addToCollection: function(){
        collection.add(this);
        $('#statement-' + this.sid).find('.add-collection, .remove-collection').remove().end().append(this.links.remove);
    },
    removeFromCollection: function(){
        collection.remove(this.sid);
        $('#statement-' + this.sid).find('.add-collection, .remove-collection').remove().end().append(this.links.add);
    },
    
});


var overlay = {
    overlay: $('<div/>', {
        id: 'overlay'
    }).appendTo('body').hide(),
    'show': function(showArrow, bodyClass){
        var body = $('body');
        this.overlay.fadeIn(150, function(){
            body.addClass('overlay');
        });
        if(showArrow) this.overlay.addClass('arrow');
        if(bodyClass !== undefined) $('body').addClass(bodyClass).data('class', bodyClass);
    },
    'hide': function(){
        var body = $('body');
        this.overlay.fadeOut(150, function(){
            body.removeClass('overlay');
            $(this).removeClass('arrow');
        });
        var bodyClass = body.data('class');
        if(bodyClass) body.removeClass(bodyClass).data('class', null);
    }
};


var loader = {
    loader: $('<div/>', {
        id: 'loader'
    }).appendTo('body').hide(),
    'show': function(){
        this.loader.show();
    },
    'hide': function(){
        this.loader.hide();
    }
};


$(document).ready(function(){
    
    window.modal = new Modal(BASE_PATH + 'intro/');
    
    /*  */
    adjustWindowSize = function(){
        var w = $(window),
            p = $('#pagebody');
        p.css('height', (w.height() - parseInt(p.css('top'))));
        $('#overlay > section').css('height', (w.height() - 225));
        $('.collection-list').css('height', (w.height() - 256));
    }
    adjustWindowSize();
    $(window).scroll(adjustWindowSize).resize(adjustWindowSize).bind('newModal', adjustWindowSize);
    
    
    window.draggable = {
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
            
            $('#pagebody .statement')
                .bind('dragstart', function(evt){
                    overlay.show(true, 'showing-collection');
                    $('#collection').addClass('dragging').animate({
                            'height': '+=15'
                        }, 175);
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
                            'height': '-=15'
                        }, 175);
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
    
    
    // Tag display
    $('.tag').live('click', function(evt){
        evt.preventDefault();
        if($(this).closest('.collection-list').length){
            $('#collection > header > h1').click();
        }else if($(this).closest('#overlay').length){
            modal.close();
        }
        var hash = slugify($(this).html());
        window.location.hash = ((hash == 'everything') ? null : hash);
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
    }).appendTo('#pagebody').hide();
    $('<a/>', {
        'href': '#',
        'id': 'next',
        'text': 'Next',
        'click': function(evt){
            evt.preventDefault();
            list.nextPage();
        }
    }).appendTo('#pagebody').hide();
    
    
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
        overlay.show(false, 'showing-collection');
        $(this).closest('#collection').animate({
            'height': $(window).height() - 93,
        }, 400);
    }, function(evt){
        evt.preventDefault();
        overlay.hide();
        $(this).closest('#collection').animate({
            'height': 10
        }, 275);
    });
    
    $('.modal-nav').live('click', function(evt){
        evt.preventDefault();
        window.modal = new Modal($(this).attr('href'));
    });
    
    $('#collection-url').live('focus', function(){
        this.select();
    });
    
    window.collection = new Collection;
    window.list = new List;
    
});