# senz.app.activity.mapping
senz user activities mapping service

## How to use this projec

### 1. prepare storm and pyleus environment

 - prepare and install [storm](http://storm.apache.org/documentation/Setting-up-development-environment.html)
 - install [pyleus](https://yelp.github.io/pyleus/)

### 2. clone this project
```sh
    $ mkdir senz.app.activity.mapping & cd senz.app.activity.mapping
    $ git clone https://github.com/tutengfei/senz.app.activity.mapping.git -b storm
```

### 3. build and run
```sh
   $ pyleus build pyleus_topology.yaml
   $ pylues run user_activity_mapping
```

### 4. see log files
You can new three terminals and see all log files.

terminal1 :

```sh
    $ tail -F /tmp/user_possible_activity.log
```

terminal2 :

```sh
    $ tail -F /tmp/mapping_user_possible_activity.log
```

terminal3 :

```sh
    $ tail -F /tmp/save_mapped_result_to_db.log
```
