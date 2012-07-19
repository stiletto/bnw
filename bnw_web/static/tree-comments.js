        jQuery.fn.swapWith = function(to) {
            return this.each(function() {
                var copy_to = $(to).clone(true);
                var copy_from = $(this).clone(true);
                $(to).replaceWith(copy_from);
                $(this).replaceWith(copy_to);
            });
        };

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

        function scroll_to_anchor() {
            if (window.location.hash) {
                $("html,body").scrollTop($(window.location.hash).offset().top);
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
                scroll_to_anchor();
                tree_comments_time = (new Date()).getTime() - tree_comments_time;
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
        });
