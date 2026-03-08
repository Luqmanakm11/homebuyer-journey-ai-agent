( function() {

	'use strict';

	//--- Get block sizes at each scroll event (slow) or only on resize event (fast)
	var GET_SIZES_ON_SCROLL = false;

	var $window            = jQuery( window ),
		$document          = jQuery( document ),
		$body              = jQuery( 'body' );

	var edit_mode = false,
		animation_allowed = true,
		motion_step   = 0,
		motion_period = 250;

	var parallax_items = [];

	$document.on( 'action.after_add_content', function( e, $cont ) {
		if ( $cont && $cont.length ) {
			$cont
				.find( '.trx_addons_parallax_layers_inited,.trx_addons_parallax_blocks_inited' )
				.removeClass( 'trx_addons_parallax_layers_inited trx_addons_parallax_blocks_inited' );
		}
	} );

	$document.on( 'action.got_ajax_response action.init_hidden_elements', function( e ) {
		// Check items after timeout to allow theme add params
		setTimeout( function() {
			var items = jQuery('.trx_addons_parallax_layers:not(.trx_addons_parallax_layers_inited)');
			if ( items.length > 0 ) {
				items.each( function() {
					var layers = new trx_addons_parallax( jQuery(this).addClass('trx_addons_parallax_layers_inited'), 'layers' );
					if ( layers.init() ) {
						parallax_items.push( layers );
					}
				} );
			}
			items = jQuery('.trx_addons_parallax_blocks:not(.trx_addons_parallax_blocks_inited)');
			if ( items.length > 0 ) {
				items.each( function() {
					var blocks = new trx_addons_parallax( jQuery(this).addClass('trx_addons_parallax_blocks_inited'), 'blocks' );
					if ( blocks.init() ) {
						parallax_items.push( blocks );
					}
				} );
			}
		}, 0 );
	} );

	$window.on( 'elementor/frontend/init', function() {
		edit_mode = Boolean( window.elementorFrontend.isEditMode() );
		// Uncomment a next line to disable animations in the Elementor Editor
		// animation_allowed = ! edit_mode;

		window.elementorFrontend.hooks.addAction( 'frontend/element_ready/section', parallax_init );
		window.elementorFrontend.hooks.addAction( 'frontend/element_ready/column',  parallax_init );
		window.elementorFrontend.hooks.addAction( 'frontend/element_ready/element', parallax_init );
		window.elementorFrontend.hooks.addAction( 'frontend/element_ready/widget',  parallax_init );
	} );

	// Create a controlling object for each target item
	function parallax_init( $init_obj ) {
		// Remove old handlers in edit mode (if Parallax is switched off)
		if ( edit_mode ) {
			parallax_remove_handlers( $init_obj );
		}
		// Init new items
		var layers = new trx_addons_parallax( $init_obj, 'layers' );
		if ( layers.init() ) {
			parallax_items.push( layers );
		}
		$init_obj.addClass('trx_addons_parallax_layers_inited');
		var blocks = new trx_addons_parallax( $init_obj, 'blocks' );
		if ( blocks.init() ) {
			parallax_items.push( blocks );
		}
		$init_obj.addClass('trx_addons_parallax_blocks_inited');
	}

	// Remove old handlers in edit mode (if Parallax is switched off)
	function parallax_remove_handlers( $init_obj ) {
		if ( animation_allowed && parallax_items.length ) {
			parallax_items = parallax_items.filter( function( item ) {
				return ! item.remove_handlers( $init_obj );
			} );
		}
	}

	// Class to control a parallax item
	window.trx_addons_parallax = function( $target, init_type ) {
		var self          = this,
			settings      = false,
			parallax_type = 'none',
			$targetLayers = $target,
			$targetBlocks = $target,
			target_id     = $target.data( 'id' );

		if ( ! target_id ) {
			target_id = 'parallax' + ( '' + Math.random() ).replace( '.', '' );
			$target.data( 'id', target_id );
		}

		var scroll_list   = [],
			mouse_list    = [],
			motion_list   = [];

		var wst           = trx_addons_window_scroll_top() + trx_addons_fixed_rows_height(),
			ww            = trx_addons_window_width(),
			wh            = trx_addons_window_height() - trx_addons_fixed_rows_height(),
			is_safari     = !!navigator.userAgent.match(/Version\/[\d\.]+.*Safari/),
			platform      = navigator.platform;

		var tl            = 0,
			tt            = 0,
			tw            = 0,
			th            = 0,
			tx            = 0,
			ty            = 0,
			cx            = 0,
			cy            = 0,
			dx            = 0,
			dy            = 0;

		self.init = function() {
			if ( ! edit_mode ) {
				if ( init_type == 'layers' ) {
					settings = $target.data( 'parallax-blocks' ) || false;
					if ( settings ) {
						parallax_type = 'layers';
					}
				} else {
					var params = $target.data( 'parallax-params' ) || false;					
					if ( params ) {
						settings = [];
						settings.push(params);
						parallax_type = 'blocks';
					}
				}
			} else {
				settings = self.get_editor_settings( $target, init_type );
			}
			if ( ! settings ) {
				return false;
			}

			// If block must catch mouse events
			if ( settings[0].mouse == 1 ) {

				parallax_type += '|layers';

				var layout_data = {
						selector: $target,
						image: false,
						size: 'auto',
						prop: settings[0].mouse_type || 'transform3d',
						type: 'mouse',
						x: 0,
						y: 0,
						z: settings[0].mouse_z || 0,
						speed: 2 * ( ( settings[0].mouse_speed ? settings[0].mouse_speed : 10 ) / 100 ),
						tilt_amount: settings[0].mouse_tilt_amount || 70,
						motion_dir: 'round',
						motion_time: 5
					};

				mouse_list.push( layout_data );
			}

			if ( init_type == 'layers' || settings[0].mouse == 1 ) {
				if ( settings[0].mouse_handler == 'window' ) {
					$targetLayers = $body;
				} else if ( settings[0].mouse_handler == 'content' ) {
					$targetLayers = jQuery( trx_addons_apply_filters( 'trx_addons_filter_page_wrap_class', TRX_ADDONS_STORAGE['page_wrap_class'] ? TRX_ADDONS_STORAGE['page_wrap_class'] : '.page_wrap', 'elementor-parallax' ) ).eq(0);
				} else if ( settings[0].mouse_handler == 'row' ) {
					if ( init_type != 'layers' ) {
						$targetLayers = $target.hasClass( 'trx_addons_parallax_blocks' )
											? $target.parent()
											: $target.parents( '.elementor-section' ).eq(0);
					}
				} else if ( settings[0].mouse_handler == 'column' ) {
					$targetLayers = $target.hasClass( 'trx_addons_parallax_blocks' )
										? $target.parent()
										: $target.parents( '.elementor-column' ).eq(0);
				} else if ( settings[0].mouse_handler == 'parent' ) {
					$targetLayers = $target.parent();
				} else if ( settings[0].mouse_handler && '.#'.indexOf( settings[0].mouse_handler.substring(0, 1) ) != -1 ) {
					$targetLayers = $target.parents( settings[0].mouse_handler );
				} else if ( settings[0].mouse_type == 'tilt' ) {
					var $tilt_trigger = $target.parents( '.trx_addons_tilt_trigger' );
					if ( $tilt_trigger.length > 0 ) {
						$targetLayers = $tilt_trigger.eq(0);
					}
				}
				$targetLayers.data('mouse-handler', settings[0].mouse_handler);
			}

			if ( parallax_type.indexOf('layers') >= 0 ) {
				if ( init_type == 'layers' ) {
					self.create_layers();
				}
				if ( animation_allowed ) {
					if ( ! $targetLayers.attr( 'data-mousemove-' + target_id ) ) {
						$targetLayers.attr( 'data-mousemove-' + target_id, target_id );
						$targetLayers.on( 'mousemove.trx_addons_parallax', self.mouse_move_handler );
						$targetLayers.on( 'mouseleave.trx_addons_parallax', self.mouse_leave_handler );
					}
					if ( motion_list.length > 0 ) {
						$targetLayers.attr( 'data-motionmove-' + target_id, setInterval( self.motion_move_handler, motion_period ) );
					}
				}
			}

			if ( parallax_type.indexOf('blocks') >= 0 ) {
				settings[0].selector = $targetBlocks;
				settings[0].hsection = $targetBlocks.parents( '.sc_hscroll_section' );
				settings[0].hscroller = settings[0].hsection.length ? settings[0].hsection.parents( '.sc_hscroll_scroller' ) : false;
				if ( settings[0].flow == 'sticky' ) {	//$targetBlocks.hasClass( 'sc_parallax_sticky' ) ) {
					$targetBlocks.css( 'top', ( 100 - settings[0].range_start ) + '%' );
				}
				scroll_list.push(settings[0]);
			}

			if ( ! GET_SIZES_ON_SCROLL ) {
				self.get_blocks_sizes();
				$document.on( 'action.init_hidden_elements', self.get_blocks_sizes );
				$document.on( 'action.sc_layouts_row_fixed_on action.sc_layouts_row_fixed_off', self.get_blocks_sizes );
				$document.on( 'action.resize_trx_addons', self.get_blocks_sizes );
			}

			$document.on( 'action.resize_trx_addons action.scroll_trx_addons', self.scroll_handler );

			if ( animation_allowed ) {
				self.scroll_update( true );
			}

			return true;
		};

		self.remove_handlers = function( $init_obj ) {
			var found = $target.is( $init_obj );
			// Remove handlers if is a checked obj
			if ( found ) {
				// Reset attribute 'style' if parallax turned off
				$target.attr( 'style', '' );
				// Delete mousemove handlers
				if ( $targetLayers.attr( 'data-mousemove-' + target_id ) ) {
					$targetLayers.removeAttr( 'data-mousemove-' + target_id );
					$targetLayers.off( 'mousemove.trx_addons_parallax', self.mouse_move_handler );
					$targetLayers.off( 'mouseleave.trx_addons_parallax', self.mouse_leave_handler );
				}
				// Stop motion
				if ( $targetLayers.attr( 'data-motionmove-' + target_id ) ) {
					clearInterval( $targetLayers.attr( 'data-motionmove-' + target_id ) );
					$targetLayers.removeAttr( 'data-motionmove-' + target_id );
				}
			}
			return found;
		};

		self.get_blocks_sizes = function() {
			jQuery.each( scroll_list, function( index, block ) {
				block.sizes = {
					width: block.selector.outerWidth(),
					height: block.selector.outerHeight(),
					top: block.selector.offset().top
				};
				if ( block.flow == 'sticky' ) {	//block.selector.hasClass( 'sc_parallax_sticky' ) ) {
					var $parent = block.selector.parent();
					block.sizes.parent_selector = $parent;
					block.sizes.parent_height = $parent.outerHeight();
					block.sizes.parent_top = $parent.offset().top;
				}
			} );
		};

		self.get_editor_settings = function( $target, init_type ) {
			if ( ! window.elementor || ! window.elementor.hasOwnProperty( 'elements' ) ) {
				return false;
			}

			var elements = window.elementor.elements;

			if ( ! elements.models ) {
				return false;
			}

			var section_id = $target.data('id'),
				section_cid = $target.data('model-cid'),
				section_data = {};

			function get_section_data( idx, obj ) {
				if ( 0 < Object.keys( section_data ).length ) {
					return;
				} else if ( section_id == obj.id ) {
					section_data = obj.attributes.settings.attributes;
				} else if ( obj.attributes && obj.attributes.elements && obj.attributes.elements.models ) {
					jQuery.each( obj.attributes.elements.models, get_section_data );
				}
			}

			jQuery.each( elements.models, get_section_data );

			if ( 0 === Object.keys( section_data ).length ) {
				return false;
			}

			var settings = [];
			
			if ( init_type == 'layers' && section_data.hasOwnProperty( 'parallax_blocks' ) ) {
				parallax_type = 'layers';
				jQuery.each( section_data[ 'parallax_blocks' ].models, function( index, obj ) {
					settings.push( obj.attributes );
				} );
			} else if ( init_type == 'blocks'
						&& ( section_data.hasOwnProperty( 'parallax' ) && section_data.parallax == 'parallax'
							||
							section_data.hasOwnProperty( 'parallax_mouse' ) && section_data.parallax_mouse == 'mouse'
							)
			) {
				parallax_type = 'blocks';
				var parallax_on = section_data.hasOwnProperty( 'parallax' ) && section_data.parallax == 'parallax',
					mouse_on = section_data.hasOwnProperty( 'parallax_mouse' ) && section_data.parallax_mouse == 'mouse';
				settings.push( {
					// Parallax settings
					type:          parallax_on && section_data.hasOwnProperty( 'parallax_type' ) ? section_data.parallax_type : 'object',
					flow:          parallax_on && section_data.hasOwnProperty( 'parallax_flow' ) ? section_data.parallax_flow : 'default',
					range_start:   parallax_on && section_data.hasOwnProperty( 'parallax_range_start' ) ? section_data.parallax_range_start.size : 0,
					range_end:     parallax_on && section_data.hasOwnProperty( 'parallax_range_end' ) ? section_data.parallax_range_end.size : 40,
					duration:      parallax_on && section_data.hasOwnProperty( 'parallax_duration' ) ? section_data.parallax_duration.size : 1,
					squeeze:       parallax_on && section_data.hasOwnProperty( 'parallax_squeeze' ) ? section_data.parallax_squeeze.size : 1,
					ease:          parallax_on && section_data.hasOwnProperty( 'parallax_ease' ) ? section_data.parallax_ease : 'power2',
					x_start:       parallax_on && section_data.hasOwnProperty( 'parallax_x_start' ) ? section_data.parallax_x_start.size : 0,
					x_end:         parallax_on && section_data.hasOwnProperty( 'parallax_x_end' ) ? section_data.parallax_x_end.size : 0,
					x_unit:        parallax_on && section_data.hasOwnProperty( 'parallax_x_start' ) ? section_data.parallax_x_start.unit : 'px',
					y_start:       parallax_on && section_data.hasOwnProperty( 'parallax_y_start' ) ? section_data.parallax_y_start.size : 0,
					y_end:         parallax_on && section_data.hasOwnProperty( 'parallax_y_end' ) ? section_data.parallax_y_end.size : 0,
					y_unit:        parallax_on && section_data.hasOwnProperty( 'parallax_y_start' ) ? section_data.parallax_y_start.unit : 'px',
					scale_start:   parallax_on && section_data.hasOwnProperty( 'parallax_scale_start' ) ? section_data.parallax_scale_start.size : 100,
					scale_end:     parallax_on && section_data.hasOwnProperty( 'parallax_scale_end' ) ? section_data.parallax_scale_end.size : 100,
					rotate_start:  parallax_on && section_data.hasOwnProperty( 'parallax_rotate_start' ) ? section_data.parallax_rotate_start.size : 0,
					rotate_end:    parallax_on && section_data.hasOwnProperty( 'parallax_rotate_end' ) ? section_data.parallax_rotate_end.size : 0,
					opacity_start: parallax_on && section_data.hasOwnProperty( 'parallax_opacity_start' ) ? section_data.parallax_opacity_start.size : 1,
					opacity_end:   parallax_on && section_data.hasOwnProperty( 'parallax_opacity_end' ) ? section_data.parallax_opacity_end.size : 1,
					// Text settings
					text:          parallax_on && section_data.hasOwnProperty( 'parallax_text' ) ? section_data.parallax_text : 'block',
					// Mouse settings
					mouse:             mouse_on ? 1 : 0,
					mouse_type:        mouse_on && section_data.hasOwnProperty( 'parallax_mouse_type' ) ? section_data.parallax_mouse_type : 'transform3d',
					mouse_tilt_amount: mouse_on && section_data.hasOwnProperty( 'parallax_mouse_tilt_amount' ) ? section_data.parallax_mouse_tilt_amount.size : 70,
					mouse_speed:       mouse_on && section_data.hasOwnProperty( 'parallax_mouse_speed' ) ? section_data.parallax_mouse_speed.size : 10,
					mouse_z:           mouse_on && section_data.hasOwnProperty( 'parallax_mouse_z' ) ? section_data.parallax_mouse_z.size : '',
					mouse_handler:     mouse_on && section_data.hasOwnProperty( 'parallax_mouse_handler' ) ? section_data.parallax_mouse_handler : 'row'
				} );
			}

			return 0 !== settings.length ? settings : false;
		};

		self.create_layers = function() {

			$target.find( '> .sc_parallax_block' ).remove();
			
			var bg_parallax_present = false;

			jQuery.each( settings, function( index, block ) {
				var image       = block['image'].url,
					speed       = block['speed'].size,
					z_index     = block['z_index'].size,
					bg_size     = block['bg_size'] ? block['bg_size'] : 'auto',
					type        = block['type'] ? block['type'] : 'none',
					anim_prop   = block['animation_prop']
									? ( ['scroll', 'motion'].indexOf(type) != -1 && block['animation_prop'] != 'background'
											? 'transform'
											: block['animation_prop']
											)
									: 'background',
					left        = block['left'].size,
					top         = block['top'].size,
					// Motion parameters
					motion_dir  = block['motion_dir'] ? block['motion_dir'] : 'round',
					motion_time = block['motion_time'] ? block['motion_time'].size : 5,
					// Mouse parameters
					tilt_amount = block['mouse_tilt_amount'] ? block['mouse_tilt_amount'].size : 70,
					mouse_handler = block['mouse_handler'] ? block['mouse_handler'] : 'row',
					// New parallax to fix Chrome scroll: used only for layers with type=='scroll' and animation type=='background'
					bg_parallax = block['bg_parallax'] && type =='scroll' && anim_prop == 'background' ? block['bg_parallax'] : false,
					$layout     = null;

				if ( bg_parallax ) {
					bg_parallax_present = true;
				}

				if ( '' !== image || 'none' !== type ) {
					var layout_init = {
						'z-index': z_index
					};
					if ( 'none' === type ) {
						layout_init['left'] = left + '%';
						layout_init['top'] = top + '%';
					}
					$layout = jQuery( '<div class="sc_parallax_block'
											+ ' sc_parallax_block_type_' + type
											+ ' sc_parallax_block_animation_' + ( bg_parallax ? 'bg_parallax' : anim_prop )
											+ (is_safari ? ' is-safari' : '')
											+ ('MacIntel' == platform ? ' is-mac' : '')
											+ (typeof block['class'] !== 'undefined' && block['class'] != '' ? ' ' + block['class'] : '')
										+ '">'
											+ '<div class="sc_parallax_block_image"'
												+ ( bg_parallax
													? ' parallax="' + ( speed / 100 ) + '"'
													: ''
													)
											+ '></div>'
										+ '</div>' )
								.prependTo( $target )
								.css( layout_init );

					layout_init = {
						'background-image': 'url(' + image + ')',
						'background-size': bg_size,
						'background-position-x': left + '%',
						'background-position-y': top + '%'
					};
					$layout.find( '> .sc_parallax_block_image' ).css(layout_init);

					var layout_data = {
						selector: $layout,
						image: image,
						size: bg_size,
						bg_parallax: bg_parallax,
						prop: anim_prop,
						type: type,
						x: left,
						y: top,
						z: z_index,
						speed: 2 * ( speed / 100 ),
						tilt_amount: tilt_amount,
						mouse_handler: mouse_handler,
						motion_dir: motion_dir,
						motion_time: motion_time
					};

					if ( 'scroll' === type ) {
						layout_data.hsection = layout_data.selector.parents( '.sc_hscroll_section' );
						layout_data.hscroller = layout_data.hsection.length ? layout_data.hsection.parents( '.sc_hscroll_scroller' ) : false;
						scroll_list.push( layout_data );
					} else if ( 'mouse' === type ) {
						mouse_list.push( layout_data );
					} else if ( 'motion' === type ) {
						motion_list.push( layout_data );
					}
				}
			});

			// Init new parallax method (to fix Google Chrome scroll)
			if ( bg_parallax_present ) {
				trx_addons_bg_parallax( $target.get(0) );
			}
		};


		// Scroll handlers
		//-------------------------------------
		var in_out_last_state = '';
		self.get_block_params = function( block ) {

			var params = trx_addons_object_merge( {}, block );

			// Prepare defaults
			if ( typeof params.type == 'undefined' ) params.type = 'object';
			if ( typeof params.flow == 'undefined' ) params.flow = 'default';
			if ( typeof params.range_start == 'undefined' ) params.range_start = 0;
			if ( typeof params.range_end == 'undefined' ) params.range_end = 40;
			if ( params.range_end <= params.range_start ) {
				params.range_end = Math.min( 100, params.range_start + params.range_end );
			}
			if ( params.flow == 'entrance' ) {
				params.range_end = 100;
			}
			if ( typeof params.duration == 'undefined' ) params.duration = 1;
			if ( typeof params.squeeze == 'undefined' ) params.squeeze = 1;
			if ( typeof params.ease == 'undefined' ) params.ease = "power2";
			if ( typeof params.x_start == 'undefined' ) params.x_start = 0;
			if ( typeof params.x_end == 'undefined' ) params.x_end = 0;
			if ( typeof params.x_unit == 'undefined' ) params.x_unit = 'px';
			if ( typeof params.y_start == 'undefined' ) params.y_start = 0;
			if ( typeof params.y_end == 'undefined' ) params.y_end = 0;
			if ( typeof params.y_unit == 'undefined' ) params.y_unit = 'px';
			if ( typeof params.scale_start == 'undefined' ) params.scale_start = 100;
			if ( typeof params.scale_end == 'undefined' ) params.scale_end = 100;
			if ( typeof params.rotate_start == 'undefined' ) params.rotate_start = 0;
			if ( typeof params.rotate_end == 'undefined' ) params.rotate_end = 0;
			if ( typeof params.opacity_start == 'undefined' ) params.opacity_start = 1;
			if ( typeof params.opacity_end == 'undefined' ) params.opacity_end = 1;
			if ( typeof params.text == 'undefined' ) params.text = 'block';

			// If an animation flow is 'In Out' - prepare Start and End Point and its values
			if ( params.flow == 'in_out' ) {
				// Calc additional offset of the block to compatibility with blocks inside a widget 'Horizontal Scroll'
				var hscroller_offset = params.hsection.length ? params.hscroller.data( 'hscroll-offset' ) || 0 : 0,
					hsection_offset  = params.hsection.length ? params.hsection.data( 'hscroll-section-offset' ) || 0 : 0;
				hscroller_offset += hsection_offset;

				var w_top      = wst + wh * ( 1 - params.range_end / 100 ),
					w_bottom   = wst + wh * ( 1 - params.range_start / 100 ),
					obj        = params.selector,
					obj_width  = params.sizes.width,
					obj_height = params.sizes.height,
					obj_top    = params.sizes.top + hscroller_offset,
					obj_bottom = obj_top + obj_height;

				if ( w_top >= obj_bottom || in_out_last_state == 'out' ) {				// Set range from range_end to 100%
					in_out_last_state = w_top >= obj_bottom ? 'out' : '';
					params.in_out_state = 'out';
					params.force = w_top < obj_bottom;
					params.range_start = params.range_end;
					params.range_end = 100;
					params.x_start = 0;
					params.y_start = 0;
					params.scale_start = 100;
					params.rotate_start = 0;
					params.opacity_start = 1;

				} else if ( w_bottom <= obj_top || in_out_last_state == 'in' ) {	// Set range from 0% to range_start
					in_out_last_state = w_bottom <= obj_top ? 'in' : '';
					params.in_out_state = 'in';
					params.force = w_bottom > obj_top;
					params.range_end = params.range_start;
					params.range_start = 0;
					params.x_end = 0;
					params.y_end = 0;
					params.scale_end = 100;
					params.rotate_end = 0;
					params.opacity_end = 1;

				} else {								// Set equal settings from range_start to range_end
					params.in_out_state = '';
					params.x_start = params.x_end = 0;
					params.y_start = params.y_end = 0;
					params.scale_start = params.scale_end = 100;
					params.rotate_start = params.rotate_end = 0;
					params.opacity_start = params.opacity_end = 1;
				}
			}
			return params;
		};

		self.scroll_handler = function( e ) {
			if ( ! animation_allowed ) {
				return;
			}
			wst = trx_addons_window_scroll_top() + trx_addons_fixed_rows_height();
			ww  = trx_addons_window_width();
			wh  = trx_addons_window_height() - trx_addons_fixed_rows_height();
			self.scroll_update();
		};

		self.scroll_update = function( force ) {

			if ( GET_SIZES_ON_SCROLL ) {
				self.get_blocks_sizes();
			}

			jQuery.each( scroll_list, function( index, block ) {

				if ( ! block.selector.is(':visible') ) return;

				// Calc additional offset of the block to compatibility with blocks inside a widget 'Horizontal Scroll'
				var hscroller_offset = block.hsection.length ? block.hscroller.data( 'hscroll-offset' ) || 0 : 0;
				var hsection_offset = block.hsection.length ? block.hsection.data( 'hscroll-section-offset' ) || 0 : 0;
				hscroller_offset += hsection_offset;

				// Section (row) layers
				if ( parallax_type.indexOf('layers') >= 0 ) {
					if ( ( ! block.bg_parallax || block.prop != 'background' ) && block.speed !== undefined ) {
						var $image     = block.selector.find( '.sc_parallax_block_image' ).eq(0),
							speed      = block.speed,
							offset_top = block.sizes.top + hscroller_offset,
							h          = block.sizes.height,
							y          = ( wst + wh - offset_top ) / h * 100;
						if ( wst < offset_top - wh) y = 0;
						if ( wst > offset_top + h)  y = 200;
						y = parseFloat( speed * y ).toFixed(1);
						if ( 'background' === block.prop ) {
							$image.css( {
								'background-position-y': 'calc(' + block.y + '% + ' + y + 'px)'
							} );
						} else {
							$image.css( {
								'transform': 'translateY(' + y + 'px)'
							} );
						}
					}
				}

				// Widgets (blocks)
				if ( parallax_type.indexOf('blocks') >= 0 ) {

					var params = self.get_block_params( block );

					var w_top         = wst + wh * ( 1 - params.range_end / 100 ),
						w_bottom      = wst + wh * ( 1 - params.range_start / 100 ),
						w_delta       = params.flow == 'entrance' ? 0 : 100,
						obj           = params.selector,
						obj_width     = params.sizes.width,
						obj_height    = params.sizes.height,
						obj_top       = params.sizes.top + hscroller_offset,
						obj_bottom    = obj_top + obj_height,
						parent_top    = params.flow == 'sticky' ? params.sizes.parent_top + hscroller_offset : 0,
						parent_bottom = params.flow == 'sticky' ? parent_top + params.sizes.parent_height    : 0;

					var entrance_complete = obj.hasClass('sc_parallax_entrance_complete'),
						bottom_delta = params.flow == 'entrance' && params.range_start == 0
											? wh * ( 1 - params.range_start / 100 ) / 10
											: 0;
					// Set a start settings for the object
					// via imitation his place at the top or bottom of the range
					var obj_visible = true;
					if ( obj.data('inited') === undefined && params.flow != 'sticky' ) {
						if ( obj_top > w_bottom ) {
							obj_top = w_bottom + w_delta - bottom_delta;
							obj_visible = false;
						} else if ( obj_bottom < w_top ) {
							obj_bottom = w_top - w_delta;
							obj_visible = false;
						}
						obj.data( 'inited', 1 );
					}

					if ( ( force || params.force )
						|| ( ! entrance_complete
								&& w_top - w_delta <= ( params.flow == 'sticky'
															? parent_bottom
															: ( params.flow == 'in_out' && params.in_out_state == 'in'
																	? obj_top
																	: obj_bottom
																	)
																)
								&& ( params.flow == 'sticky'
										? parent_top
										: ( params.flow == 'in_out' && params.in_out_state == 'out'
												? obj_bottom
												: obj_top
											)
										) <= w_bottom + w_delta - bottom_delta
							)
					) {
						if ( params.flow == 'entrance' ) {
							var entrance_start = false;
							if ( ! obj.data( 'entrance-inited' ) ) {
								// Old way: If a top of the object is over than the bottom side of the window - mark it as complete
//								if ( obj_top < w_bottom - bottom_delta ) {
								// New way: If a bottom of the object is over than the top side of the window - mark it as complete
								if ( obj_bottom <= w_top - w_delta ) {
									obj.addClass('sc_parallax_entrance_complete');
									//return;
								} else {
									entrance_start = true;
								}
								obj.data( 'entrance-inited', 1 );
							} else if ( ! obj.hasClass('sc_parallax_entrance_complete') ) {
								obj.addClass('sc_parallax_entrance_complete');
							}
						}

						var delta, shift;
						if ( params.flow == 'entrance' ) {
							delta = 1;
							shift = entrance_start ? 0 : 1;
						} else if ( params.flow == 'sticky' ) {
							var obj_anchor = obj_top + Math.round( obj_height * ( 100 - params.range_start ) / 100 );
							delta = Math.max( 1, parent_bottom - obj_bottom );
							shift = Math.max( 0, w_bottom - obj_anchor );
							if ( force ) {
								block.selector.css( 'top', 'calc( ' + ( 100 - params.range_start ) + '% - ' + ( obj_anchor - obj_top ) + 'px )' );
							}
						} else if ( params.flow == 'in_out' ) {
							delta = Math.max( 1, wh * ( params.range_end - params.range_start ) / 100 );
							shift = w_bottom - ( params.in_out_state == 'in' ? obj_top : obj_bottom );
						} else {
							delta = Math.max( 1, wh * ( params.range_end - params.range_start ) / 100 + obj_height );
							shift = w_bottom - obj_top;
						}

						var step_x = params.x_start != params.x_end ? ( params.x_end - params.x_start ) / delta : 0,
							step_y = params.y_start != params.y_end ? ( params.y_end - params.y_start ) / delta : 0,
							step_scale = params.scale_start != params.scale_end ? ( params.scale_end - params.scale_start ) / 100 / delta : 0,
							step_rotate = params.rotate_start != params.rotate_end ? ( params.rotate_end - params.rotate_start ) / delta : 0,
							step_opacity = params.opacity_start != params.opacity_end ? ( params.opacity_end - params.opacity_start ) / delta : 0;

						var scroller_init = {
												overwrite: true,
												ease: self.get_ease( params.ease )
											},
//							transform = '',
							val = false;

						if ( step_x !== 0 ) {
							val = Math.round( params.x_start + shift * step_x );	// - (params.type == 'bg' && params.x > 0 ? params.x : 0)
							if ( params.x_start < params.x_end && val < params.x_start || params.x_start > params.x_end && val > params.x_start ) {
								val = params.x_start;
							}
							if ( params.x_start < params.x_end && val > params.x_end || params.x_start > params.x_end && val < params.x_end ) {
								val = params.x_end;
							}
//							transform += 'translateX(' + val + params.x_unit + ')';
							scroller_init.x = val + params.x_unit;
						}

						if ( step_y !== 0 ) {
							val = Math.round( params.y_start + shift * step_y );	// - (params.type == 'bg' && params.y > 0 ? params.y : 0)
							if ( params.y_start < params.y_end && val < params.y_start || params.y_start > params.y_end && val > params.y_start ) {
								val = params.y_start;
							}
							if ( params.y_start < params.y_end && val > params.y_end || params.y_start > params.y_end && val < params.y_end ) {
								val = params.y_end;
							}
//							transform += ( transform != '' ? ' ' : '' ) + 'translateY(' + val + params.y_unit + ')';
							scroller_init.y = val + params.y_unit;
						}

						if ( step_rotate !== 0 ) {
							val = trx_addons_round_number( params.rotate_start + shift * step_rotate, 2);
							if ( params.rotate_start < params.rotate_end && val < params.rotate_start || params.rotate_start > params.rotate_end && val > params.rotate_start ) {
								val = params.rotate_start;
							}
							if ( params.rotate_start < params.rotate_end && val > params.rotate_end || params.rotate_start > params.rotate_end && val < params.rotate_end ) {
								val = params.rotate_end;
							}
//							transform += ( transform != '' ? ' ' : '' ) + 'rotate(' + val + 'deg)';
							scroller_init.rotation = val;
						}

						if ( step_scale !== 0 ) {
							val = trx_addons_round_number( params.scale_start / 100 + shift * step_scale, 2 );	//- (params.type == 'bg' && params.scale < 0 ? params.scale / 100 : 0)
							if ( params.scale_start < params.scale_end && val < params.scale_start / 100 || params.scale_start > params.scale_end && val > params.scale_start / 100 ) {
								val = params.scale_start / 100;
							}
							if ( params.scale_start < params.scale_end && val > params.scale_end / 100 || params.scale_start > params.scale_end && val < params.scale_end / 100 ) {
								val = params.scale_end / 100;
							}
//							transform += ( transform != '' ? ' ' : '' ) + 'scale(' + val + ')';
							scroller_init.scale = val;
						}

						if ( step_opacity !== 0 ) {
							val = trx_addons_round_number( params.opacity_start + shift * step_opacity, 2 );
							if ( params.opacity_start < params.opacity_end && val < params.opacity_start || params.opacity_start > params.opacity_end && val > params.opacity_start ) {
								val = params.opacity_start;
							}
							if ( params.opacity_start < params.opacity_end && val > params.opacity_end || params.opacity_start > params.opacity_end && val < params.opacity_end ) {
								val = params.opacity_end;
							}
							scroller_init.opacity = Math.max( 0, Math.min( 1, val ) );
						}

						// Save a current transform object to data-param
						obj.data( 'trx-parallax-scroller-init', scroller_init );

						// Prepare (split) text with 'by words' and 'by chars' effects
						if ( [ 'chars', 'words'].indexOf( params.text ) != -1 && obj.data('element_type') !== undefined ) {
							var sc = ( obj.data('element_type') == 'widget' ? obj.data('widget_type') : obj.data('element_type') ).split('.')[0],
								inner_obj = obj.find('.sc_parallax_text_block');
							if ( inner_obj.length === 0 ) {
								inner_obj = obj.find(
											sc == 'trx_sc_title'
												? '.sc_item_title_text,.sc_item_subtitle'
												: ( sc == 'trx_sc_supertitle'
													? '.sc_supertitle_text'
													: ( sc == 'heading'
														? '.elementor-heading-title'
														: 'p'
														)
													)
											);
								if ( inner_obj.length > 0 ) {
									inner_obj.each( function( idx ) {
										inner_obj.eq( idx )
											.html(
												params.text == 'chars'
													? self.wrap_chars( inner_obj.eq( idx ).html(), true )
													: self.wrap_words( inner_obj.eq( idx ).html() )
											);
									} );
									inner_obj = inner_obj.find('.sc_parallax_text_block');
								}
							}
							if ( inner_obj.length > 0 ) {
								obj = inner_obj;
							}
						}

						// If any property is changed
						if ( val !== false ) {
							// if ( force && obj_visible ) {
							// 	// Set a start transform for each object if it is visible in the viewport
							// 	var css_init = {
							// 		'translate': 'none',
							// 		'rotate': 'none',
							// 		'scale': 'none',
							// 		'transform': transform
							// 	};
							// 	if ( scroller_init.opacity !== undefined ) {
							// 		css_init.opacity = scroller_init.opacity;
							// 	}
							// 	obj.css( css_init );
							// } else {
								// Animate each object
								obj.each( function(idx) {
									if ( idx === 0 || ( force && obj_visible ) ) {
										TweenMax.to( obj.eq( idx ), force && obj_visible ? 0 : params.duration, scroller_init );
									} else {
										setTimeout( function() {
											TweenMax.to( obj.eq( idx ), params.duration, scroller_init );
										}, ( params.text == 'chars' ? 75 : 250 ) * idx * params.squeeze );
									}
								} );
							// }
						}
					}
				}
			} );
		};


		// Mouse move/leave handlers
		//-----------------------------------------
		self.mouse_move_handler = function( e ) {
			if ( tw === 0 ) {
				tl = $targetLayers.offset().left;
				tt = $targetLayers.offset().top;
				tw = $targetLayers.width();
				th = ['window', 'content'].indexOf($targetLayers.data('mouse-handler'))!=-1
						? Math.min(trx_addons_window_height(), $targetLayers.height())
						: $targetLayers.height();
			}
			wst = trx_addons_window_scroll_top() + trx_addons_fixed_rows_height();
			ww  = trx_addons_window_width();
			wh  = trx_addons_window_height() - trx_addons_fixed_rows_height();
			
			cx  = Math.ceil( tw / 2 );	// + tl,
			cy  = Math.ceil( th / 2 );	// + tt,
			dx  = e.clientX - tl - cx;
			dy  = ['window', 'content'].indexOf($targetLayers.data('mouse-handler'))!=-1
						? e.clientY - cy
						: e.clientY + wst - tt - cy;
			tx  = -1 * ( dx / cx );
			ty  = -1 * ( dy / cy );

			jQuery.each( mouse_list, self.mouse_move_update );
		};

		self.mouse_leave_handler = function( e ) {
			jQuery.each( mouse_list, function( index, block ) {
				var $image = block.selector.find( '.sc_parallax_block_image' ).eq(0);
				if ( $image.length === 0 ) {
					$image = block.selector;
				}

				var x = 0, y = 0, z = 0;

				// Add scroll parameters
				var scroller_init = block.selector.data( 'trx-parallax-scroller-init' );
				if ( scroller_init && scroller_init.css ) {
					x = x * 1 + trx_addons_units2px( scroller_init.css.x || 0, block );
					y = y * 1 + trx_addons_units2px( scroller_init.css.y || 0, block );
				}

				if ( block.prop == 'background' ) {
					TweenMax.to(
						$image,
						1.5,
						{
							overwrite: true,
							backgroundPositionX: block.x + '%',
							backgroundPositionY: block.y + '%',
							ease: Power2.easeOut
						}
					);
				} else if ( block.prop == 'transform' ) {
					TweenMax.to(
						$image,
						1.5,
						{
							overwrite: true,
							x: x,
							y: y,
							ease:Power2.easeOut
						}
					);
				} else if ( block.prop == 'transform3d' ) {
					TweenMax.to(
						$image,
						1.5,
						{
							overwrite: true,
							x: x,
							y: y,
							z: z,
							rotationX: 0,
							rotationY: 0,
							ease:Power2.easeOut
						}
					);
				} else if ( block.prop == 'tilt' ) {
					TweenMax.to(
						$image,
						0.2,
						{
							overwrite: true,
							x: x,
							y: y,
							z: z,
							rotationX: 0,
							rotationY: 0,
							scale: 1,
							transformPerspective: 1500,
							ease:Power2.easeOut
						}
					);
				}

			} );
		};

		self.mouse_move_update = function( index, block, time, ease ) {
			var	$image   = block.selector.find( '.sc_parallax_block_image' ).eq(0),
				speed    = block.speed,
				x        = parseFloat( tx * 125 * speed ).toFixed(1),
				y        = parseFloat( ty * 125 * speed ).toFixed(1),
				z        = block.z * 50,
				rotate_x = parseFloat( tx * 25 * speed ).toFixed(1),
				rotate_y = parseFloat( ty * 25 * speed ).toFixed(1);

			// Add scroll parameters
			var scroller_init = block.selector.data( 'trx-parallax-scroller-init' );
			if ( scroller_init && scroller_init.css ) {
				x = x * 1 + trx_addons_units2px( scroller_init.css.x || 0, block );
				y = y * 1 + trx_addons_units2px( scroller_init.css.y || 0, block );
			}

			if ( $image.length === 0 ) {
				$image = block.selector;
			}

			if ( block.prop == 'background' ) {
				TweenMax.to(
					$image,
					time === undefined ? 1 : time,
					{
						overwrite: true,
						backgroundPositionX: 'calc(' + block.x + '% + ' + x + 'px)',
						backgroundPositionY: 'calc(' + block.y + '% + ' + y + 'px)',
						ease: ease === undefined ? Power2.easeOut : ease
					}
				);
			} else if ( block.prop == 'transform' ) {
				TweenMax.to(
					$image,
					time === undefined ? 1 : time,
					{
						overwrite: true,
						x: x,
						y: y,
						ease: ease === undefined ? Power2.easeOut : ease
					}
				);
			} else if ( block.prop == 'transform3d' ) {
				TweenMax.to(
					$image,
					time === undefined ? 2 : time,
					{
						overwrite: true,
						x: x,
						y: y,
						z: z,
						rotationX: rotate_y,
						rotationY: -rotate_x,
						ease: ease === undefined ? Power2.easeOut : ease
					}
				);
			} else if ( block.prop == 'tilt' ) {
				var m = block.tilt_amount > 0 ? block.tilt_amount : 70,
					k = ['window', 'content'].indexOf($targetLayers.data('mouse-handler')) != -1 ? 2 : 4;
				z = Math.max(0, block.z);
				if ( isNaN(z) ) z = 0;
				TweenMax.set( $image,
					{
						transformOrigin: ((dx + cx) * 25 / tw + 40) + "% " + ((dy + cy) * 25 / th + 40) + "%",
						transformPerspective: 1000 + 500 * z
					}
				);
				TweenMax.to(
					$image,
					time === undefined ? 0.5 : time,
					{
						overwrite: true,
						rotationX:  dy / ( m - k * z ),	// ( m - 2 * z )	//( m * ( z + 2 ) / 2 )
						rotationY: -dx / ( m - k * z ),	// ( m - 2 * z )	//( m * ( z + 2 ) / 2 )
						y: ty * 2 * z,
						x: tx * 2 * z,
						z: 2 * z,
						scale: 1 + z / 100,
						ease: ease === undefined ? Power2.easeOut : ease
					}
				);
			}
		};


		// Permanent motion handlers
		//-----------------------------------------
		self.motion_move_handler = function() {
			if ( tw === 0 ) {
				tl = $targetLayers.offset().left;
				tt = $targetLayers.offset().top;
				tw = $targetLayers.width();
				th = $targetLayers.height();
			}
			cx = Math.ceil( tw / 2 );	// + tl,
			cy = Math.ceil( th / 2 );	// + tt;
			jQuery.each( motion_list, function( index, block ) {
				var fi,
					delta = ( ( motion_period * motion_step++ ) % ( block['motion_time'] * 1000 ) ) / ( block['motion_time'] * 1000 ),
					angle = 2 * Math.PI * delta;
				if ( block['motion_dir'] == 'round' ) {
					fi = Math.atan2(tw / 2 * Math.sin(angle), th / 2 * Math.cos(angle));
					dx = tw / 2 * Math.cos(fi);
					dy = th / 2 * Math.sin(fi);
				} else if ( block['motion_dir'] == 'random' ) {
					dx = -tw + tw * 2 * Math.random();
					dy = -th + th * 2 * Math.random();
				} else {
					dx = block['motion_dir'] == 'vertical' ? 0 : tw / 2 * Math.cos(angle);
					dy = block['motion_dir'] == 'horizontal' ? 0 : th / 2 * Math.sin(angle);
				}
				tx = -1 * ( dx / cx );
				ty = -1 * ( dy / cy );
				if ( block['motion_dir'] == 'random' ) {
					if ( delta === 0 ) {
						self.mouse_move_update(index, block, block['motion_time'], Power0.easeNone);
					}
				} else {
					self.mouse_move_update(index, block, block['motion_time'], block['motion_dir'] == 'round' ? Power0.easeNone : Power2.easeOut );
				}
			} );
		};


		// Utilities
		//-----------------------------------------

		// Return easing method from its name
		self.get_ease = function(name) {
			name = name.toLowerCase();
			if ( name == 'none' || name == 'line' || name == 'linear' || name == 'power0' )
				return Power0.easeNone;
			else if ( name == 'power1')
				return Power1.easeOut;
			else if ( name == 'power2')
				return Power2.easeOut;
			else if ( name == 'power3')
				return Power3.easeOut;
			else if ( name == 'power4')
				return Power4.easeOut;
			else if ( name == 'back')
				return Back.easeOut;
			else if ( name == 'elastic')
				return Elastic.easeOut;
			else if ( name == 'bounce')
				return Bounce.easeOut;
			else if ( name == 'rough')
				return Rough.easeOut;
			else if ( name == 'slowmo')
				return SlowMo.easeOut;
			else if ( name == 'stepped')
				return Stepped.easeOut;
			else if ( name == 'circ')
				return Circ.easeOut;
			else if ( name == 'expo')
				return Expo.easeOut;
			else if ( name == 'sine')
				return Sine.easeOut;
		};

		// Wrap each char to the <span>
		self.wrap_chars = function(txt, wrap_words) {
			return trx_addons_wrap_chars( txt,
											'<span class="sc_parallax_text_block">',
											'</span>',
											wrap_words ? '<span class="sc_parallax_word_wrap">' : '',
											wrap_words ? '</span>' : ''
										);
		};

		// Wrap each word to the <span>
		self.wrap_words = function(txt) {
			return trx_addons_wrap_words( txt, '<span class="sc_parallax_text_block">', '</span>' );
		};

	};


	// New parallax (to fix Google Chrome scroll)
	// CSS transform3D and perspective are used instead shift background position on scroll events
	// This method needs a special layout:
	// 	body (with overflow hidden)
	// 		.viewport (with overflow-y: scroll | auto and height: 100%)
	//			.parallax_wrap
	//				.parallax_image
	//				.parallax_image
	//				.parallax_image
	//				...
	//----------------------------------------------------------------------------
	window.trx_addons_bg_parallax = function(clip) {
		var parallax        = clip.querySelectorAll('.sc_parallax_block_image[parallax]'),
			parallaxDetails = [],
			sticky          = false;
		
		// Edge requires a transform on the document body and a fixed position element
		// in order for it to properly render the parallax effect as you scroll.
		// See https://developer.microsoft.com/en-us/microsoft-edge/platform/issues/5084491/
//		if (getComputedStyle(document.body).transform == 'none') {
			// Broke page in WordPress - admin bar shift down and margin-top is appear in the body
//			document.body.style.transform = 'translateZ(0)';
//		}

		var fixedPos = document.createElement('div');
		fixedPos.style.position = 'fixed';
		fixedPos.style.top = '0';
		fixedPos.style.width = '1px';
		fixedPos.style.height = '1px';
		fixedPos.style.zIndex = 1;
		document.body.insertBefore(fixedPos, document.body.firstChild);

		for ( var i = 0; i < parallax.length; i++ ) {
			var elem = parallax[i];
			var container = elem.parentNode;
			if ( getComputedStyle(container).overflow != 'visible' ) {
				console.error('Need non-scrollable container to apply perspective for', elem);
				continue;
			}
			if ( clip && container.parentNode != clip ) {
				console.warn('Currently we only track a single overflow clip, but elements from multiple clips found.', elem);
			}
			clip = container.parentNode;
			if (getComputedStyle(clip).overflow == 'visible') {
				console.error('Parent of sticky container should be scrollable element', elem);
			}
			// TODO(flackr): optimize to not redo this for the same clip/container.
			var perspectiveElement;
			if (sticky || getComputedStyle(clip).webkitOverflowScrolling) {
				sticky = true;
				perspectiveElement = container;
			} else {
				perspectiveElement = clip;
				container.style.transformStyle = 'preserve-3d';
			}
			perspectiveElement.style.perspectiveOrigin = 'bottom right';
			perspectiveElement.style.perspective = '1px';
			if (sticky) {
				elem.style.position = '-webkit-sticky';
				elem.style.top = '0';
			}
			elem.style.transformOrigin = 'bottom right';
			// Find the previous and next elements to parallax between.
			var previousCover = parallax[i].previousElementSibling;
			while (previousCover && previousCover.hasAttribute('parallax')) {
				previousCover = previousCover.previousElementSibling;
			}
			var nextCover = parallax[i].nextElementSibling;
			while (nextCover && !nextCover.hasAttribute('parallax-cover')) {
				nextCover = nextCover.nextElementSibling;
			}
			parallaxDetails.push( {
				'node': parallax[i],
				'top': parallax[i].offsetTop,
				'sticky': !!sticky,
				'nextCover': nextCover,
				'previousCover': previousCover
			} );
		}

		for ( i = 0; i < parallax.length; i++ ) {
			parallax[i].parentNode.insertBefore(parallax[i], parallax[i].parentNode.firstChild);
		}

		// Add a scroll listener to hide perspective elements when they should no longer be visible.
		clip.addEventListener( 'scroll', function() {
			for (var i = 0; i < parallaxDetails.length; i++) {
				var container = parallaxDetails[i].node.parentNode;
				var previousCover = parallaxDetails[i].previousCover;
				var nextCover = parallaxDetails[i].nextCover;
				var parallaxStart = previousCover ? (previousCover.offsetTop + previousCover.offsetHeight) : 0;
				var parallaxEnd = nextCover ? nextCover.offsetTop : container.offsetHeight;
				var threshold = 200;
				var visible = parallaxStart - threshold - clip.clientHeight < clip.scrollTop &&
				parallaxEnd + threshold > clip.scrollTop;
				// FIXME: Repainting the images while scrolling can cause jank.
				// For now, keep them all.
				// var display = visible ? 'block' : 'none'
				var display = 'block';
				if (parallaxDetails[i].node.style.display != display) {
					parallaxDetails[i].node.style.display = display;
				}
			}
		} );

		var bg_parallax_resize = function(details) {
			for (var i = 0; i < details.length; i++) {
				var container = details[i].node.parentNode;
				var clip = container.parentNode;
				var previousCover = details[i].previousCover;
				var nextCover = details[i].nextCover;
				var rate = details[i].node.getAttribute('parallax');
				var parallaxStart = previousCover ? (previousCover.offsetTop + previousCover.offsetHeight) : 0;
				var scrollbarWidth = details[i].sticky ? 0 : clip.offsetWidth - clip.clientWidth;
				var parallaxElem = details[i].sticky ? container : clip;
				var height = details[i].node.offsetHeight;
				var depth = 0;
				if ( rate ) {
					depth = 1 - (1 / rate);
				} else {
					var parallaxEnd = nextCover ? nextCover.offsetTop : container.offsetHeight;
					depth = (height - parallaxEnd + parallaxStart) / (height - clip.clientHeight);
				}
				if ( details[i].sticky ) {
					depth = 1.0 / depth;
				}
				var scale = 1.0 / (1.0 - depth);
				// The scrollbar is included in the 'bottom right' perspective origin.
				var dx = scrollbarWidth * (scale - 1);
				// Offset for the position within the container.
				var dy = details[i].sticky
							? -(clip.scrollHeight - parallaxStart - height) * (1 - scale)
							: (parallaxStart - depth * (height - clip.clientHeight)) * scale;
				details[i].node.style.transform = 'scale(' + (1 - depth) + ') translate3d(' + dx + 'px, ' + dy + 'px, ' + depth + 'px)';
			}
		};

		window.addEventListener('resize', bg_parallax_resize.bind(null, parallaxDetails));
		bg_parallax_resize(parallaxDetails);

	};

}() );
