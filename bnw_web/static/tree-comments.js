        jQuery.fn.swapWith = function(to) {
            return this.each(function() {
                var copy_to = $(to).clone(true);
                var copy_from = $(this).clone(true);
                $(to).replaceWith(copy_from);
                $(this).replaceWith(copy_to);
            });            
        };
        
        function sort_comments() {
            // ем говно, сосу хуи
            var roc=true;
            while (roc) {
                roc=false;
                $("div.comments div.outerborder").each(function (i,o) {
                    var cur=$(o);
                    var next=cur.next();
                    if (next.length==0) return;

                    var curid=message_id+"/"+cur.attr("id");
                    var nextid=message_id+"/"+next.attr("id");

                    if (comment_info[curid].sorter>comment_info[nextid].sorter) {
                        //$(".msg").append("Exchange "+cur.attr("id")+" ------- "+next.attr("id")+"<br/>");
                        cur.swapWith(next);
                        if($("#"+cur.attr("id")).length==0)
                            alert("Lost cur "+cur.attr("id"));
                        if($("#"+next.attr("id")).length==0)
                            alert("Lost next "+next.attr("id"));
                        roc=true;
                    }
                })
            }
        }
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
                    //var c=$(o);
                    var cmt_id = message_id+"/"+o.getAttribute("id");
                    /*var margin=comment_info[cmt_id].depth;
                    if (margin>15) margin=15;
                    c.css("margin-left",margin+"em");*/
                    comments_html[cmt_id]=o.innerHTML;
                });
                var element_idx = 0;
                $("div.comments div.outerborder").each(function (i,o) { 
                    var cmt_id = comments_order[element_idx][0];
                    var cmt_html = comments_html[cmt_id];

                    o.innerHTML = cmt_html;
                    o.setAttribute("id",cmt_id.split("/")[1]);

                    var margin=comment_info[cmt_id].depth;
                    if (margin>15) margin=15;
                    o.setAttribute("style","margin-left: "+margin+"em;");
                    element_idx++;
                });
                //sort_comments();
                tree_comments_time = (new Date()).getTime() - tree_comments_time;
        }
        
        var commentinfo_generate_time;
        $(function(){
            commentinfo_generate_time = (new Date()).getTime();
            commentinfo_generate();
            commentinfo_generate_time = (new Date()).getTime() - commentinfo_generate_time;

            if (comment_count) {
                if ( comment_count > 50 ) {
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
            
            
            var ws = new WebSocket(websocket_base+window.location.pathname);
            ws.onmessage = function (e) {
                var d=JSON.parse(e.data);
                var new_comment=$("<div class='comment'>").text(d.text);
                var addinfo=$("<div>").text("#"+d['id']+" / @"+d['user']);
                if (d['replyto'])
                    addinfo.append(' --> '+d['replyto']);
                new_comment.append(addinfo);
                $("div.comments").append($("<div class='outerborder'>").append(new_comment));
            };
            
        });
