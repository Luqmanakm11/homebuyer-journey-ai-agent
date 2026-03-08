var trx_popup = jQuery(".trx_popup"); 
var trx_popup_delay = trx_popup.data('delay'); 
var trx_popup_interval = trx_popup.data('refresh-interval'); 

jQuery(window).on('load', function()  {        
        'use strict';   
        setTimeout(function() {
            trx_popup_open_close(); 
        }, trx_popup_delay * 1000);
    });

function trx_popup_open_close()  {
    'use strict';    

    // Close
    jQuery(".trx_popup_close").on('click', function()  {  
        trx_popup.addClass('close');
        setTimeout(function()  {    
            trx_popup.remove();
        }, 1000);
    });

    // Set/remove cache
    if ( trx_popup.hasClass("has-cache") ) {
        jQuery(".trx_popup_close").on('click', function()  { 
            jQuery.cookie('trx-popup-has-cache', 'true', { expires: trx_popup_interval });
        });
    } else {
        jQuery.removeCookie('trx-popup-has-cache')
    }

    if ( jQuery.cookie('trx-popup-has-cache') == 'true' ) {
        trx_popup.hide();
    } else {
        jQuery(".trx_popup.publish").show();
    }
}