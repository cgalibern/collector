function app_start() {
  i18n_init(_app_start)
}

function _app_start() {
  $(document).i18n()
  search("layout_search_tool")
  services_feed_self_and_group()
  fset_selector("fset_selector")
  app_bindings()
  app_menu_entries_bind_click_to_load()
}

function app_load_href(href) {
    // loadable co-functions ends with '_load'
    event.preventDefault()
    var _href

    if (href.match(/:\/\//)) {
      // full url
      var fn_idx = 5
    } else {
      // relative url
      var fn_idx = 3
    }

    // http:, , host:port, app, ctrl, fn, arg0, arg1, ... lastarg?key=val,key=val
    var l = href.split("?")
    var v = l[0].split("/")

    v[fn_idx] += "_load"

    l[0] = v.join("/")
    _href = l.join("?")

    console.log("load", _href)
    $(".layout").load(_href, {}, function (responseText, textStatus, req) {
      if (textStatus == "error") {
        // load error
        console.log("fallback to location", href)
        document.location.replace(href)
      } else {
        // load success, purge tables not displayed anymore
        for (tid in osvc.tables) {
          if ($('#'+tid).length == 0) {
            delete osvc.tables[tid]
            if (tid in wsh) {
              delete wsh[tid]
            }
          }
        }
      }
    })
}

function app_menu_entries_bind_click_to_load() {
  $(".menu .menu_entry").bind("click", function(event) {
    var href = $(this).find("a").attr("href")
    if (!href) {
      return
    }
    app_load_href(href)
    $(".header .menu").hide("fold")

    // update browser url and history
    history.pushState({}, "", href)
  
    // prevent default
    return false
  })
}


function app_bindings() {
  // Handle navigation between load()ed pages through browser tools 
  $(window).on("popstate", function(e) {
    if (e.originalEvent.state !== null) {
      app_load_href(location.href);
    }
  })

  // disable browser context menu expect on canvases (topology, ...)
  $(document).on('click', function(event){
    if(event.which == 2){
      event.preventDefault()
    }
  })
  $(document).on('contextmenu', function(event){
    if ($(event.target).is("canvas")) {
      return
    }
    event.preventDefault()
  })
  
  // key bindings
  $(document).keydown(function(event) {
    // ESC closes pop-ups and blur inputs
    if ( event.which == 27 ) {
      $("input:focus").blur()
      $("textarea:focus").blur()
      $("#overlay").empty()
      $(".white_float").hide()
      $(".white_float_input").hide()
      $(".right_click_menu").hide()
      osvc_popup_remove_from_stack();
      /*$(".extraline").remove()
      $(".menu").hide("fold")
      $(".menu").find("[id^=sextra]").remove()
      */
      $("#search_input").val("")
      return
    }
  
    // 'TAB' from search input focuses the first visible menu_entry
    if (event.which == 9) {
      if ($('#search_input').is(":focus")) {
        $(".header").find(".menu_entry:visible").first().addClass("menu_selected")
      }
    }

    // don't honor shortcuts if a input is focused
    if ($('input').is(":focus")) {
      return
    }
    if ($('textarea').is(":focus")) {
      return
    }
  

    //
    // shortcuts
    //

    // 'f' for search
    if (event.which == 70) {
      if (!$('#search_input').is(":focus")) {
        event.preventDefault();
        $("[name=fset_selector]").click()
      }
    }

    // 's' for search
    else if (event.which == 83) {
      if (!$('#search_input').is(":focus")) {
        event.preventDefault();
        $('#search_input').val('');
      }
      $('#search_input').focus();
    }

    // 'n' for search
    else if (event.which == 78) {
      event.preventDefault();
      $(".header").find(".menu16").parents("ul").first().siblings(".menu").show("fold", function(){filter_menu()});
      $('#search_input').val('');
      $('#search_input').focus();
    }

    // Left
    else if (event.which == 37) {
      event.preventDefault();
      var entries = $(".header").find(".menu_entry:visible");
      var i = 0;
      var prev;
      entries.each(function(){
        i += 1;
        if ($(this).hasClass("menu_selected")) {
          if (i==1) { return; }
          entries.removeClass("menu_selected");
          $(prev).addClass("menu_selected");
          return;
        }
        prev = this;
      });
    }

    // Up
    else if (event.which == 38) {
      event.preventDefault();
      var entries = $(".header").find(".menu_entry:visible");
      var selected = entries.filter(".menu_selected")
      var selected_index = entries.index(selected)
      var candidate_entries = entries.slice(0, selected_index)
      if (selected.length == 0) {
        selected = entries.first()
      }
      if (candidate_entries.length == 0) {
        candidate_entries = entries
      }
      candidate_entries.filter(function(i, e){
        if ($(this).position().left == selected.position().left) {
          return true
        }
        return false
      }).last().each(function(){
        entries.removeClass("menu_selected");
        $(this).addClass("menu_selected");
        return;
      });
    }

    // Right
    else if (event.which == 39) {
      event.preventDefault();
      var entries = $(".header").find(".menu_entry:visible");
      var i = 0;
      var found = false;
      entries.each(function(){
        i += 1;
        if ($(this).hasClass("menu_selected")) {
          if (i==entries.length) { return; }
          found = true;
          return;
        }
        if (found) {
          entries.removeClass("menu_selected");
          $(this).addClass("menu_selected");
          found = false;
          return;
        }
      });
    }

    // Down
    else if (event.which == 40) {
      event.preventDefault();
      var entries = $(".header").find(".menu_entry:visible");
      var selected = entries.filter(".menu_selected")
      var selected_index = entries.index(selected)
      var candidate_entries = entries.slice(selected_index+1)
      if (selected.length == 0) {
        selected = entries.first()
      }
      if (candidate_entries.length == 0) {
        candidate_entries = entries
      }
      candidate_entries.filter(function(i, e){
        if ($(this).position().left == selected.position().left) {
          return true
        }
        return false
      }).first().each(function(){
        entries.removeClass("menu_selected");
        $(this).addClass("menu_selected");
        return;
      });
    }

    // 'Enter' from a menu entry does a click
    else if (is_enter(event)) {
      $(".header").find(".menu_selected:visible").each(function(){
        event.preventDefault();;
        $(this).effect("highlight");
        $(this).trigger("click")
      })
    }
  });
}


