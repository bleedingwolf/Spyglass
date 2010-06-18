
var mouse_coords = null;

$(document).ready( function() {
    $('select.spyglass-dropdown').each( function(idx, el) {
        setupDropdown($(el));
    });
    
    fixHowStupidGeckoIs();
    
    $('input.url-input').keyup(warnAboutNoHttps);
    
    if($('body').hasClass('create-session-page')) {
        $('.hidden-at-page-load').hide();
        $('html').mousemove(fadeInOtherControls);
    }
    
    var url_value = $('#create-session-header-form .url-input').val();
    setSelectionRange($('#create-session-header-form .url-input')[0], url_value.length, url_value.length);
});

function setSelectionRange(textElem, selectionStart, selectionEnd) {
    // copy-pasta from http://bytes.com/topic/javascript/answers/151663-changing-selected-text-textarea
    if (textElem.setSelectionRange) { // FF
    
        window.setTimeout( function(x,posL, posR) { // bug 265159
            return function(){ x.setSelectionRange(posL, posR); };
        }(textElem, selectionStart, selectionEnd), 100);
        
    } else if (textElem.createTextRange) { // IE
    
        var range = textElem.createTextRange();
        range.collapse(true);
        range.moveEnd('character', selectionEnd);
        range.moveStart('character', selectionStart);
        range.select();
    }
}


function fixHowStupidGeckoIs() {
    if($.browser.mozilla) {
        var current = $('.spyglass-dropdown').css('font-size');
        current = current.replace('px', '');
        var fixed = (parseInt(current) + 1) + 'px';
        $('.spyglass-dropdown').css('font-size', fixed);
        $('.spyglass-dropdown .option').css('font-size', fixed);
    }
}

function fadeInOtherControls(event) {
    var event_coords = {x: event.pageX, y: event.pageY };

    if(mouse_coords != null) {
        if(!coordsAreEqual(mouse_coords, event_coords)) {
            $('.hidden-at-page-load').fadeIn(500);
            $('html').unbind('mousemove', fadeInOtherControls);
        }
    }
    mouse_coords = event_coords;
}

function coordsAreEqual(a, b) {
    return (a.x == b.x && a.y == b.y);
}

function setupDropdown(select) {
        
    var input = $(document.createElement('input'));
    input.attr('type', 'hidden');
    input.attr('name', select.attr('name'));
        
    var text_wrapper = $(document.createElement('span'));
    text_wrapper.css('margin-right', '10px');
    
    var container = $(document.createElement('div'));
    container.addClass('option-container');
    container.hide();
    
    var dropdown = $(document.createElement('div'));
    dropdown.addClass('spyglass-dropdown');
    
    dropdown.append(input);
    dropdown.append(text_wrapper);
    dropdown.append(container);
    
    select.replaceWith(dropdown);
        
    var dropdownWasDefocused = function(event) {
        event.stopPropagation();
        container.hide();
        $(document).unbind('click', dropdownWasDefocused);
    }
    
        
    $('option', select).each( function(idx, opt) {
        opt = $(opt);
        
        if(opt.attr('selected')) {
            input.val(opt.text());
            text_wrapper.text(opt.text());
        }
        
        var new_opt = $(document.createElement('span'));
        new_opt.appendTo(container);

        new_opt.addClass('option');
        new_opt.text(opt.text());
        new_opt.width(80);

        new_opt.css('display', 'block');
        new_opt.css('padding-right', '20px');
        
        new_opt.click( function(event) {
    
            event.stopPropagation();
            
            var selected_value = $(this).text();
            input.val(selected_value);
            text_wrapper.text(selected_value);
            
            container.hide();
            $(document).unbind('click', dropdownWasDefocused);
        })
    })
    
    dropdown.click( function(event) {
        event.stopPropagation();
        container.show();
        
        $(document).bind('click', dropdownWasDefocused);
    });
    
}

function warnAboutNoHttps(event) {
    var input = $(this);
    var warning = $('.https-warning');
    if(warning.size() == 0) {
        
        warning = $(document.createElement('div')).addClass('https-warning');
        var offset = input.offset();
        offset.top += (input.height() + 12);
        offset.left += 1;
        warning.css(offset);
        warning.text("Sorry, Spyglass doesn't support HTTPS requests yet.");
        
        $('body').append(warning);
    }
    
    if(input.val().indexOf("https") === 0) {
        warning.show();
    } else {
        warning.hide();
    }
}
