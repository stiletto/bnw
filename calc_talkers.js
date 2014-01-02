
mapfun = function () {
    //var dt = new Date(this.date * 1000);
    //var dn = dt.getFullYear() * 10000 + (1 + dt.getMonth()) * 100 + dt.getDate();
    emit(this.user, this.text.length);
}

redfun = function (k, vals) {
    var sum = 0;
    for (var i in vals) {
        sum += vals[i];
    }
    return sum;
}

db.comments.mapReduce(mapfun,redfun,{out:{replace: 'stat_talkers'}});
db.messages.mapReduce(mapfun,redfun,{out:{reduce: 'stat_talkers', nonAtomic: true}});
