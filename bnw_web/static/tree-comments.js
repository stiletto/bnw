        jQuery.fn.swapWith = function(to) {
            return this.each(function() {
                var copy_to = $(to).clone(true);
                var copy_from = $(this).clone(true);
                $(to).replaceWith(copy_from);
                $(this).replaceWith(copy_to);
            });
        };

        function comment_reply() {
            $(".msgid").each(function (i,o) {
                var cur=$(o);
                var text=cur.text();
                var lp = text.split('/');
                if ((lp[1])&&(lp[0]=="#"+message_id)) {
                    cur.click(function () {
                        $("[name=comment]").val($(this).text().split('/')[1]);
                    });
                }
            });
        }
        function textarea_press(event) {
            if (event.ctrlKey && (event.keyCode==13 || event.keyCode==10))
                $("#commentform").submit();
        }

        var comments_order = [];
        function comments_order_compare(a,b) {
            var as=a[1]; var bs=b[1];
            var cl=0;
            if (as.length<bs.length)
                cl=as.length;
            else
                cl=bs.length;
            var i;
            for (i=0;i<cl;i++)
                if(as[i]!=bs[i]) return as[i]-bs[i];
            return as.length-bs.length;
        }

        var comments_max_depth=0;
        function commentinfo_generate() {
            var updating = true;
            comments_order = [];
            while (updating) {
                updating = false;
                for (k in comment_info) {
                    var v = comment_info[k];
                    if (v.depth==undefined) {
                        if (!v.replyto) {
                            v.depth = 0;
                            v.sorter = [v.num];
                        } else {
                            var parent = comment_info[v.replyto];
                            if (!parent) {
                                v.depth = 0;
                                v.sorter = [v.num];
                                v.orphan = true;
                            } else {
                                if (parent.depth!=undefined) {
                                    v.depth = parent.depth+1;
                                    v.sorter = parent.sorter.concat([v.num]);
                                }
                            }
                        }
                        if (v.depth!=undefined) {
                            if (v.depth>comments_max_depth)
                                comments_max_depth = v.depth;
                            comments_order.push([k,v.sorter]);
                        }
                        updating = true;
                    }
                }
            }
        }

        var tree_comments_time;
        function tree_comments() {
                tree_comments_time = (new Date()).getTime();
                var comments_html={};
                comments_order.sort(comments_order_compare);
                $("div.comments div.outerborder").each(function (i,o) {
                    var cmt_id = message_id+"/"+o.getAttribute("id");
                    comments_html[cmt_id]=o.innerHTML;
                });
                var element_idx = 0;
                var margin_ratio = 32.0 / comments_max_depth;
                if (comments_max_depth>50)
                    margin_ratio = 32.0 / 50;
                if (margin_ratio > 1) margin_ratio = 1;
                $("div.comments div.outerborder").each(function (i,o) {
                    var cmt_id = comments_order[element_idx][0];
                    var cmt_html = comments_html[cmt_id];

                    o.innerHTML = cmt_html;
                    o.setAttribute("id",cmt_id.split("/")[1]);

                    var margin=comment_info[cmt_id].depth;
                    if (margin>50)
                        margin=50;
                    margin = margin * margin_ratio;

                    o.setAttribute("style","margin-left: "+margin+"em;");
                    element_idx++;
                });
                tree_comments_time = (new Date()).getTime() - tree_comments_time;
        }

        function api_call_alert(func,args) {
            args['login']=$.cookie("bnw_loginkey");
            $.ajax({ url: "/api/"+func,
                data:args,
                dataType:'json',
                success: function (data) {
                    if (data.ok)
                        alert("OK. "+data.desc);
                    else
                        alert("ERROR. "+data.desc);
                },
                error: function (data,status) {
                    alert("API request failed.");
                    return false;
                }
            });
        }

        var add_message_actions_time;
        function add_message_actions() {
            add_message_actions_time = (new Date()).getTime();
            var isloggedin = $.cookie("bnw_loginkey")!=null;
                $(".msgb, .cmtb").each(function (i,o) {
                    var id = o.getAttribute("id").split("-")[1];
                    var ismsg = id.indexOf("/")==-1;
                    var jo = $(o);
                    $(o).html(" ");
                    if (ismsg&&isloggedin)
                        jo.append( $("<a/>").text("r").click(function () { api_call_alert("recommend",{message:id}); }) );
                });
            add_message_actions_time = (new Date()).getTime() - add_message_actions_time;
        }

        var commentinfo_generate_time;
        $(function(){
            commentinfo_generate_time = (new Date()).getTime();
            commentinfo_generate();
            commentinfo_generate_time = (new Date()).getTime() - commentinfo_generate_time;

            if (comment_count) {
                if ( comment_count > 200 ) {
                    $(".somenote").html("В этом треде слишком много комментариев. Ваш браузер <a href='#' id='force_tree'>не лопнет</a> от их отображения в виде дерева?");
                    $("#force_tree").click(function () {
                        $(".somenote").css("display","none");
                        tree_comments();
                    });
                    $(".somenote").css("display","block");
                } else if (!window.location.search || (window.location.search.indexOf("notree")==-1)) {
                    tree_comments();
                }
            }
            comment_reply();


            add_message_actions();

            var favicon_changed = false;
            $(window).focus(function () {
                if (favicon_changed) {
                    favicon.change("/favicon.ico");
                    favicon_changed = false;
                }
            });


            var ws_addr = 'ws://'+websocket_base+window.location.pathname+'/ws';
            var ws;
            var ws_double_fail = false
            function openws() {
                if ("WebSocket" in window) {
                    ws = new WebSocket(ws_addr);
                } else {
                    ws = new MozWebSocket(ws_addr);
                }

                ws.onopen = function () {
                    if (ws_double_fail)
                        $("#ws_status").text("WS Active (again)");
                    else
                        $("#ws_status").text("WS Active");
                    ws_double_fail = false;
                }
                ws.onclose = function () {
                    $("#ws_status").text("WS Closed");
                    reopenws();
                }
                ws.onerror = function () {
                    $("#ws_status").text("WS Error");
                    reopenws();
                }
                ws.onmessage = function (e) {
                    var d=JSON.parse(e.data);
                    var new_comment=$("<div class='comment'>").text(d.text);
                    var addinfo=$("<div>").text("#"+d['id']+" / @"+d['user']);
                    if (d['replyto'])
                        addinfo.append(' --> '+d['replyto']);
                    new_comment.append(addinfo);
                    $("div.comments").append($("<div class='outerborder'>").append(new_comment));
                    if (!favicon_changed) {
                        favicon.change("/static/favicon-event.ico");
                        favicon_changed = true;
                    }
                }

                return ws;
            }
            function reopenws() {
                if (!ws_double_fail) {
                    ws_double_fail = true;
                    openws();
                }
            }
            openws();

        });
