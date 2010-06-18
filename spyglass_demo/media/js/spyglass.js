
$(document).ready(function(){
    $('select.spyglass-dropdown').each( function(idx, el) {
        setupDropdown($(el));
    });
    
    $('input.url-input').keyup(warnAboutNoHttps);
    
    fixHowStupidGeckoIs();
});

function fixHowStupidGeckoIs() {
    if($.browser.mozilla) {
        var current = $('.spyglass-dropdown').css('font-size');
        current = current.replace('px', '');
        var fixed = (parseInt(current) + 1) + 'px';
        console.log(fixed);
        $('.spyglass-dropdown').css('font-size', fixed);
    }
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
