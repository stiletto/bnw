print('digraph G{');
db.subscriptions.find({type:'sub_user'},{user:1,target:1}).forEach(function (a) { print('"'+a['target']+'" -> "'+a['user']+'";')});
print('}')
