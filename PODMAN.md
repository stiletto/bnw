# Playing with BnW in podman

## Building

```sh
$ podman build -t bnw .
```

## Running

```sh
$ bash podman-run.sh
```

Then navigate to http://localhost:7808/

## Adding users

```sh
$ podman run --rm --pod bnw -ti mongo:3.6 mongo
> use bnw
> function bnwNewUser(name) { db.users.insert({id: UUID().hex(), name: name, 'login_key': name, 'regdate': (new Date())/1000, jid: name + '@localhost', jids: [name + '@localhost'], interface: 'redeye', 'settings': {'password': name}}) }
> ['abc', 'loh','pidor', 'huesos'].forEach((x) => bnwNewUser(x))
```

## Cleaning up

```sh
$ podman pod kill bnw
$ podman pod rm bnw
```
