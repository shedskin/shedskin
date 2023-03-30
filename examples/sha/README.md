# sha

This example requires the `openssl` library and headers to be installed.

```
shedskin build -Xlib --long -lcrypto sha
build/sha some_text
```


## for Linux

```bash
sudo apt install libssl-dev

```


## for macOS

This works if you homebrew:

```bash
brew install openssl
```

Of course, you can install it manually, but the above is easiest.
