export RUSTFLAGS := "-D warnings"
export RUSTDOCFLAGS := "-D warnings"

[private]
default:
    just -l --unsorted

###########
### RUN ###
###########

# Run (local) CI
ci: (ci_impl ""           ""               ) \
    (ci_impl ""           " --all-features") \
    (ci_impl " --release" ""               ) \
    (ci_impl " --release" " --all-features")

[private]
ci_impl mode features: (check_impl mode features) (test_impl mode features)

# Check syntax, formatting, clippy, deny, semver, ...
check: (check_impl ""           ""               ) \
       (check_impl ""           " --all-features") \
       (check_impl " --release" ""               ) \
       (check_impl " --release" " --all-features")

[private]
check_impl mode features: (cargo_check mode features) \
                          (cargo_hack mode) \
                          cargo_fmt \
                          (cargo_clippy mode features) \
                          cargo_deny

[private]
cargo_check mode features:
    cargo check --workspace --all-targets{{ mode }}{{ features }}
    cargo doc --no-deps --document-private-items --keep-going{{ mode }}{{ features }}

[private]
cargo_hack mode: install_cargo_hack
    cargo hack check --workspace --all-targets{{ mode }}

[private]
cargo_fmt: install_rust_nightly install_rust_nightly_fmt
    cargo +nightly fmt --check

[private]
cargo_clippy features mode: install_cargo_clippy
    cargo clippy --workspace --all-targets{{ features }}{{ mode }}

[private]
cargo_deny: install_cargo_deny
    cargo deny check

# Test multiple configurations
test: (test_impl ""           ""               ) \
      (test_impl ""           " --all-features") \
      (test_impl " --release" ""               ) \
      (test_impl " --release" " --all-features")

[private]
test_impl mode features: (cargo_test mode features)

[private]
cargo_test features mode:
    cargo test \
    --workspace \
    --all-targets\
    {{ features }}\
    {{ mode }}

# Audit advisories, bans, licenses, and sources
audit: cargo_deny

# Build and test bindings
bindings: bindings_python

# Build and test Python bindings
bindings_python: install_python_black install_python_maturin install_python_mypy install_python_ruff
    # Remove any old wheels
    rm -rf target/wheels/*
    # Lint Python code using Black and Ruff
    python -m black --check .
    python -m ruff check
    # Build Python extension
    maturin build --release
    # Install extension and run unit tests
    pip install --force-reinstall --find-links=target/wheels/ imap_codec
    python -m unittest -v
    # Perform static type checking using mypy
    python -m mypy .

###############
### INSTALL ###
###############

# Install required tooling (ahead of time)
install: install_rust_nightly \
         install_rust_nightly_fmt \
         install_cargo_clippy \
         install_cargo_deny \
         install_cargo_hack \
         install_python_black \
         install_python_maturin \
         install_python_mypy \
         install_python_ruff

[private]
install_rust_nightly:
    rustup toolchain install nightly --profile minimal

[private]
install_rust_nightly_fmt:
    rustup component add --toolchain nightly rustfmt

[private]
install_cargo_clippy:
    rustup component add clippy

[private]
install_cargo_deny:
    cargo install --locked cargo-deny

[private]
install_cargo_hack:
    cargo install --locked cargo-hack

[private]
install_python_black:
    python -m pip install -U black

[private]
install_python_maturin:
    python -m pip install -U maturin

[private]
install_python_mypy:
    python -m pip install -U mypy

[private]
install_python_ruff:
    python -m pip install -U ruff
