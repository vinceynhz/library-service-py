# library-service-py
A Python version of the library service leveraging Flask

This project uses virtual environments. After cloning repo run

```
make dev-init
```

This will setup the local virtual environment, activate it, install requirements and
install the current project as a dependency as well.

For new sessions on the command line, the following can be run:

```
make dev
```

This enables the virtual environment for development

To run testing
```
make test
```

For prod install
```
make init
```