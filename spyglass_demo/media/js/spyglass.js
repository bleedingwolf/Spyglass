
var mouse_coords = null;

$(document).ready( function() {
    setupHttpSessionForm();
    setupPageFadeIn();
    setupAutoReloadingSessionPage();
});

function setupHttpSessionForm() {
    $('select.spyglass-dropdown').each( function(idx, el) {
        setupDropdown($(el));
    });
    
    fixHowStupidGeckoIs();
    
    var url_value = $('#create-session-header-form .url-input').val();
    setSelectionRange($('#create-session-header-form .url-input')[0], url_value.length, url_value.length);
    
    $('.advanced-options table.extra-headers').after('<p class="add-extra-header-link"><a href="#">add another</a></p>');
    $('.advanced-options .add-extra-header-link').click( function(e) {
        e.preventDefault();
        
        var current_form_count = $('#id_header-TOTAL_FORMS').val();
        current_form_count++;
    
        const TEMPLATE = '<tr><td><input type="text" name="header-__prefix__-name" id="id_header-__prefix__-name" /></td><td><input type="text" name="header-__prefix__-value" id="id_header-__prefix__-value" /></td></tr>';
        var row_html = TEMPLATE.replace(/__prefix__/g, current_form_count);
        
        $('#id_header-TOTAL_FORMS').val(current_form_count);
        
        var table = $('table.extra-headers');
        console.log(table);
        table.append(row_html);
    })
    
    $('.advanced-form-toggle').click( function(e) {
        var current_text = $(this).text();
        if(current_text == 'Advanced Options')
            $(this).text('Basic Options');
        else
            $(this).text('Advanced Options');
        $('.advanced-options').toggle();
        e.preventDefault();
    })
}

function setupAutoReloadingSessionPage() {
    
    var placeholder = $('.loading-placeholder')
    var session_id = placeholder.attr('session_id');
    if(session_id === undefined) return;
    
    var url = '/sessions/' + session_id + '/is_complete.json';
    
    var checkWithServer = function() {

        $.getJSON(url, function(data) {
        
            if(data.complete === 'true') {
                
                if(data.error) {
                    console.log("spyglass: Request had error: %d", data.error)
                    var error_msg = $(document.createElement('p'));
                    error_msg.text('Error: ' + data.error);
                    error_msg.addClass('http-error');
                    $('.response.session-listing').replaceWith(error_msg);
                } else {
                    placeholder.replaceWith(data.pretty_response);
                    $('.response .linenos pre code').text(data.response_linenos);
                    $('.response .datetime').html('completed in ' + data.elapsed_milliseconds +
                        ' <abbr title="milliseconds">ms</abbr>')
                }
            } else {
                setTimeout(checkWithServer, 1000);
            }
        });    
    }
    
    setTimeout(checkWithServer, 1000);
}

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

    var increaseByPixels = function(elem, prop, px) {
        var current = elem.css(prop);
        current = current.replace('px', '');
        var fixed = (parseInt(current) + px) + 'px';
        elem.css(prop, fixed);    
    }

    if($.browser.mozilla) {
        increaseByPixels($('.form-bar-wrapper button'), 'padding-top', 1);
        increaseByPixels($('.form-bar-wrapper button'), 'padding-bottom', 1);
    }
}

function setupPageFadeIn() {

    $('body.create-session-page #create-session-header-form h3').addClass('hidden-at-page-load');
    $('body.create-session-page #create-session-header-form .under-input:not(.advanced)').addClass('hidden-at-page-load');

    $('.hidden-at-page-load').hide();
    $('html').mousemove(fadeInOtherControls);
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
    container.css('display', 'none');
    
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
